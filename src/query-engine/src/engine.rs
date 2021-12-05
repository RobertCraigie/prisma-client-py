/// This file has been modified from https://github.com/prisma/prisma-engines/blob/master/query-engine/query-engine-node-api/src/engine.rs
use crossbeam_channel;
use datamodel::{diagnostics::ValidatedConfiguration, Datamodel};
use opentelemetry::global;
use prisma_models::DatamodelConverter;
use query_core::{executor, schema_builder, BuildMode, QueryExecutor, QuerySchema, TxId};
use request_handlers::{GraphQlBody, GraphQlHandler, PrismaResponse};
use std::time::Duration;
use std::{
    collections::{BTreeMap, HashMap},
    path::{Path, PathBuf},
    sync::Arc,
};
use tokio::{runtime::Runtime, sync::RwLock};
use tracing::Level;
use tracing_opentelemetry::OpenTelemetrySpanExt;

use crate::{error::ApiError, logger::ChannelLogger};
use crate::{Executor, Result};

/// The main engine, that can be cloned between threads
#[derive(Clone)]
pub struct QueryEngine {
    pub inner: Arc<RwLock<Inner>>,
}

// Wrapper over the main engine, provides a blocking synchronous interface
pub struct BlockingQueryEngine {
    inner: Arc<QueryEngine>,
    runtime: Runtime,
}

/// The state of the engine.
pub enum Inner {
    /// Not connected, holding all data to form a connection.
    Builder(EngineBuilder),
    /// A connected engine, holding all data to disconnect and form a new
    /// connection. Allows querying when on this state.
    Connected(ConnectedEngine),
}

/// Holding the information to reconnect the engine if needed.
#[derive(Debug, Clone)]
struct EngineDatamodel {
    datasource_overrides: Vec<(String, String)>,
    ast: Datamodel,
    raw: String,
}

/// Everything needed to connect to the database and have the core running.
pub struct EngineBuilder {
    datamodel: EngineDatamodel,
    config: ValidatedConfiguration,
    logger: ChannelLogger,
    config_dir: PathBuf,
    env: HashMap<String, String>,
}

/// Internal structure for querying and reconnecting with the engine.
pub struct ConnectedEngine {
    datamodel: EngineDatamodel,
    query_schema: Arc<QuerySchema>,
    executor: Executor,
    logger: ChannelLogger,
    config_dir: PathBuf,
    env: HashMap<String, String>,
}

pub struct TelemetryOptions {
    enabled: bool,
    endpoint: Option<String>,
}

impl ConnectedEngine {
    /// The schema AST for Query Engine core.
    pub fn query_schema(&self) -> &Arc<QuerySchema> {
        &self.query_schema
    }

    /// The query executor.
    pub fn executor(&self) -> &(dyn QueryExecutor + Send + Sync) {
        &*self.executor
    }
}

impl BlockingQueryEngine {
    pub fn new(engine: Arc<QueryEngine>) -> Self {
        Self {
            inner: engine,
            runtime: Runtime::new().unwrap(),
        }
    }

    pub fn connect(&self, timeout: u64) -> Result<()> {
        let handle = self.runtime.handle();
        let engine = self.inner.clone();
        let (tx, rx) = crossbeam_channel::bounded(1);

        handle.spawn(async move {
            let res = engine.connect().await;
            let _ = tx.send(res);
        });

        rx.recv_timeout(Duration::from_secs(timeout))?
    }

    pub fn disconnect(&self) -> Result<()> {
        let handle = self.runtime.handle();
        let engine = self.inner.clone();
        let (tx, rx) = crossbeam_channel::bounded(1);

        handle.spawn(async move {
            let res = engine.disconnect().await;
            let _ = tx.send(res);
        });

        let _ = rx.recv()?;
        Ok(())
    }

    pub fn query_str(
        &self,
        query: String,
        trace: HashMap<String, String>,
        tx_id: Option<String>,
    ) -> Result<String> {
        let handle = self.runtime.handle();
        let engine = self.inner.clone();
        let (tx, rx) = crossbeam_channel::bounded(1);

        handle.spawn(async move {
            let res = engine.query_str(query, trace, tx_id).await;
            let _ = tx.send(res);
        });

        let res = rx.recv()??;
        Ok(res)
    }
}

impl QueryEngine {
    pub fn new(
        env: HashMap<String, String>,
        datamodel: String,
        log_level: String,
        log_queries: bool,
        datasource_overrides: BTreeMap<String, String>,
        ignore_env_var_errors: bool,
    ) -> Result<Self> {
        let config_dir = Path::new(".").to_path_buf();

        // TODO: support configuring from python
        let telemetry = TelemetryOptions {
            enabled: false,
            endpoint: None,
        };

        let overrides: Vec<(_, _)> = datasource_overrides.into_iter().collect();

        let config = if ignore_env_var_errors {
            datamodel::parse_configuration(&datamodel)
                .map_err(|errors| ApiError::conversion(errors, &datamodel))?
        } else {
            datamodel::parse_configuration(&datamodel)
                .and_then(|mut config| {
                    config
                        .subject
                        .resolve_datasource_urls_from_env(&overrides, |key| {
                            env.get(key).map(ToString::to_string)
                        })?;

                    Ok(config)
                })
                .map_err(|errors| ApiError::conversion(errors, &datamodel))?
        };

        config
            .subject
            .validate_that_one_datasource_is_provided()
            .map_err(|errors| ApiError::conversion(errors, &datamodel))?;

        let ast = datamodel::parse_datamodel(&datamodel)
            .map_err(|errors| ApiError::conversion(errors, &datamodel))?
            .subject;

        let datamodel = EngineDatamodel {
            ast,
            raw: datamodel,
            datasource_overrides: overrides,
        };

        let logger = if telemetry.enabled {
            ChannelLogger::new_with_telemetry(telemetry.endpoint)
        } else {
            ChannelLogger::new(&log_level, log_queries)
        };

        let builder = EngineBuilder {
            datamodel,
            config,
            logger,
            config_dir,
            env,
        };

        Ok(Self {
            inner: Arc::new(RwLock::new(Inner::Builder(builder))),
        })
    }

    pub async fn connect(&self) -> Result<()> {
        let mut inner = self.inner.write().await;

        match *inner {
            Inner::Builder(ref builder) => {
                let engine = builder
                    .logger
                    .clone()
                    .with_logging(|| async move {
                        let template = DatamodelConverter::convert(&builder.datamodel.ast);

                        // We only support one data source & generator at the moment, so take the first one (default not exposed yet).
                        let data_source =
                            builder.config.subject.datasources.first().ok_or_else(|| {
                                ApiError::configuration("No valid data source found")
                            })?;

                        let preview_features: Vec<_> =
                            builder.config.subject.preview_features().iter().collect();
                        let url = data_source
                            .load_url_with_config_dir(&builder.config_dir, |key| {
                                builder.env.get(key).map(ToString::to_string)
                            })
                            .map_err(|err| {
                                crate::error::ApiError::Conversion(
                                    err,
                                    builder.datamodel.raw.clone(),
                                )
                            })?;

                        let (db_name, executor) =
                            executor::load(data_source, &preview_features, &url).await?;
                        let connector = executor.primary_connector();
                        connector.get_connection().await?;

                        // Build internal data model
                        let internal_data_model = template.build(db_name);

                        let query_schema = schema_builder::build(
                            internal_data_model,
                            BuildMode::Modern,
                            true, // enable raw queries
                            data_source.capabilities(),
                            preview_features,
                        );

                        Ok(ConnectedEngine {
                            datamodel: builder.datamodel.clone(),
                            query_schema: Arc::new(query_schema),
                            logger: builder.logger.clone(),
                            executor,
                            config_dir: builder.config_dir.clone(),
                            env: builder.env.clone(),
                        })
                    })
                    .await?;

                *inner = Inner::Connected(engine);

                Ok(())
            }
            Inner::Connected(_) => Err(ApiError::AlreadyConnected),
        }
    }

    /// Disconnect and drop the core. Can be reconnected later with `#connect`.
    pub async fn disconnect(&self) -> crate::Result<()> {
        let mut inner = self.inner.write().await;

        match *inner {
            Inner::Connected(ref engine) => {
                let config = datamodel::parse_configuration(&engine.datamodel.raw)
                    .map_err(|errors| ApiError::conversion(errors, &engine.datamodel.raw))?;

                let builder = EngineBuilder {
                    datamodel: engine.datamodel.clone(),
                    logger: engine.logger.clone(),
                    config,
                    config_dir: engine.config_dir.clone(),
                    env: engine.env.clone(),
                };

                *inner = Inner::Builder(builder);

                Ok(())
            }
            Inner::Builder(_) => Err(ApiError::NotConnected),
        }
    }

    pub async fn query(
        &self,
        query: String,
        trace: HashMap<String, String>,
        tx_id: Option<String>,
    ) -> crate::Result<PrismaResponse> {
        match *self.inner.read().await {
            Inner::Connected(ref engine) => {
                engine
                    .logger
                    .with_logging(|| async move {
                        let cx = global::get_text_map_propagator(|propagator| {
                            propagator.extract(&trace)
                        });
                        let span = tracing::span!(Level::TRACE, "query");

                        span.set_parent(cx);

                        let body: GraphQlBody = serde_json::from_str(&query)?;
                        let handler = GraphQlHandler::new(engine.executor(), engine.query_schema());
                        Ok(handler.handle(body, tx_id.map(TxId::from)).await)
                    })
                    .await
            }
            Inner::Builder(_) => Err(ApiError::NotConnected),
        }
    }

    /// Helper method returning a JSON object from query()
    pub async fn query_str(
        &self,
        query: String,
        trace: HashMap<String, String>,
        tx_id: Option<String>,
    ) -> crate::Result<String> {
        Ok(serde_json::to_string(
            &self.query(query, trace, tx_id).await?,
        )?)
    }
}
