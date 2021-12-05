use std::sync::Arc;

use opentelemetry::sdk::trace::Tracer;
use tracing_opentelemetry::OpenTelemetryLayer;
use tracing_subscriber::layer::Layered;

use super::{channel::EventChannel, registry::EventRegistry};

type TelemetryLayer = Layered<
    EventChannel,
    Layered<OpenTelemetryLayer<EventRegistry, Tracer>, EventRegistry>,
    Layered<OpenTelemetryLayer<EventRegistry, Tracer>, EventRegistry>,
>;

#[derive(Clone)]
pub struct WithTelemetry {
    inner: Arc<TelemetryLayer>,
}

impl WithTelemetry {
    pub fn new(inner: TelemetryLayer) -> Self {
        Self { inner: Arc::new(inner) }
    }
}

impl tracing::Subscriber for WithTelemetry {
    fn enabled(&self, metadata: &tracing::Metadata<'_>) -> bool {
        self.inner.enabled(metadata)
    }

    fn new_span(&self, span: &tracing::span::Attributes<'_>) -> tracing::Id {
        self.inner.new_span(span)
    }

    fn record(&self, span: &tracing::Id, values: &tracing::span::Record<'_>) {
        self.inner.record(span, values)
    }

    fn record_follows_from(&self, span: &tracing::Id, follows: &tracing::Id) {
        self.inner.record_follows_from(span, follows)
    }

    fn event(&self, event: &tracing::Event<'_>) {
        self.inner.event(event)
    }

    fn enter(&self, span: &tracing::Id) {
        self.inner.enter(span)
    }

    fn exit(&self, span: &tracing::Id) {
        self.inner.exit(span)
    }
}
