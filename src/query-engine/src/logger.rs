mod channel;
mod registry;
mod telemetry;
mod visitor;

use channel::EventChannel;
use opentelemetry::{
    global,
    sdk::{propagation::TraceContextPropagator, trace::Config, Resource},
    KeyValue,
};
use registry::EventRegistry;
use std::future::Future;
use telemetry::WithTelemetry;
use tracing_futures::WithSubscriber;
use tracing_subscriber::{
    layer::{Layered, SubscriberExt},
    EnvFilter,
};

#[derive(Clone)]
enum Subscriber {
    Normal(Layered<EventChannel, EventRegistry>),
    WithTelemetry(WithTelemetry),
}

/// A logger logging to a bounded channel. When in scope, all log messages from
/// the scope are stored to the channel, which must be consumed or after some
/// point, further log lines will just be dropped.
#[derive(Clone)]
pub struct ChannelLogger {
    subscriber: Subscriber,
}

impl ChannelLogger {
    /// Creates a new instance of a logger with the minimum log level.
    pub fn new(level: &str, log_queries: bool) -> Self {
        let mut filter = EnvFilter::new(level);

        if log_queries {
            filter = filter.add_directive("quaint[{is_query}]".parse().unwrap());
        }

        let event_channel = EventChannel::new(filter, false);
        let subscriber = EventRegistry::new().with(event_channel);

        let subscriber = Subscriber::Normal(subscriber);

        Self { subscriber }
    }

    /// Creates a new instance of a logger with the `trace` minimum level.
    /// Enables tracing events to OTLP endpoint.
    pub fn new_with_telemetry(endpoint: Option<String>) -> Self {
        let event_channel = EventChannel::new(EnvFilter::new("trace"), true);

        global::set_text_map_propagator(TraceContextPropagator::new());

        // A special parameter for Jaeger to set the service name in spans.
        let resource = Resource::new(vec![KeyValue::new("service.name", "query-engine-node-api")]);
        let config = Config::default().with_resource(resource);

        let mut builder = opentelemetry_otlp::new_pipeline().with_trace_config(config);

        if let Some(endpoint) = endpoint {
            builder = builder.with_endpoint(endpoint);
        }

        let (tracer, _) = builder.install().unwrap();

        let telemetry_layer = tracing_opentelemetry::layer().with_tracer(tracer);
        let registry = EventRegistry::new()
            .with(telemetry_layer)
            .with(event_channel);
        let with_telemetry = WithTelemetry::new(registry);

        let subscriber = Subscriber::WithTelemetry(with_telemetry);

        Self { subscriber }
    }

    /// Wraps a future to a logger, storing all events in the pipeline to
    /// the channel.
    pub async fn with_logging<F, U, T>(&self, f: F) -> crate::Result<T>
    where
        U: Future<Output = crate::Result<T>>,
        F: FnOnce() -> U,
    {
        match self.subscriber {
            Subscriber::Normal(ref subscriber) => f().with_subscriber(subscriber.clone()).await,
            Subscriber::WithTelemetry(ref subscriber) => {
                f().with_subscriber(subscriber.clone()).await
            }
        }
    }
}
