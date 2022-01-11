use std::{
    collections::{BTreeMap, HashMap},
    sync::Arc,
};

use pyo3::{prelude::*, types::PyString};

use crate::engine::{BlockingQueryEngine, QueryEngine};

#[pyclass(subclass)]
pub struct PythonEngine {
    // TODO: does this need a mutex?
    inner: Arc<QueryEngine>,
    sync_engine: BlockingQueryEngine,
}

#[pymethods]
impl PythonEngine {
    #[new]
    fn new(
        env: HashMap<String, String>,
        datamodel: String,
        log_level: String,
        log_queries: bool,
        datasource_overrides: BTreeMap<String, String>,
        ignore_env_var_errors: bool,
    ) -> PyResult<Self> {
        let engine = Arc::new(QueryEngine::new(
            env,
            datamodel,
            log_level,
            log_queries,
            datasource_overrides,
            ignore_env_var_errors,
        )?);
        Ok(Self {
            inner: engine.clone(),
            sync_engine: BlockingQueryEngine::new(engine),
        })
    }

    fn connect_sync(&self, _py: Python, timeout: u64) -> PyResult<()> {
        Ok(self.sync_engine.connect(timeout)?)
    }

    fn disconnect_sync(&self, _py: Python) -> PyResult<()> {
        Ok(self.sync_engine.disconnect()?)
    }

    fn query_sync(&self, _py: Python, query: String) -> PyResult<String> {
        Ok(self.sync_engine.query_str(query, HashMap::new(), None)?)
    }

    fn connect<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        let engine = self.inner.clone();
        pyo3_asyncio::tokio::future_into_py(py, async move {
            engine.connect().await?;
            Python::with_gil(|py| Ok(py.None()))
        })
    }

    fn disconnect<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        let engine = self.inner.clone();
        pyo3_asyncio::tokio::future_into_py(py, async move {
            engine.disconnect().await?;
            Python::with_gil(|py| Ok(py.None()))
        })
    }

    // TODO: support transactions
    // TODO: support passing traces from python

    fn query<'p>(&self, py: Python<'p>, query: String) -> PyResult<&'p PyAny> {
        let engine = self.inner.clone();
        pyo3_asyncio::tokio::future_into_py(py, async move {
            let result = engine.query_str(query, HashMap::new(), None).await?;

            Ok(Python::with_gil(|py| {
                let x = PyString::new(py, &result);
                let any: &PyAny = x.as_ref();
                any.to_object(py)
            }))
        })
    }
}
