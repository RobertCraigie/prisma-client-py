use std::sync::Arc;

use tracing::{
    span::{Attributes, Record},
    Event, Id, Metadata, Subscriber,
};
use tracing_subscriber::{
    registry::{Data, LookupSpan},
    Registry,
};

#[derive(Clone)]
pub struct EventRegistry {
    inner: Arc<Registry>,
}

impl Default for EventRegistry {
    fn default() -> Self {
        Self::new()
    }
}

impl EventRegistry {
    pub fn new() -> Self {
        Self {
            inner: Arc::new(Registry::default()),
        }
    }
}

impl<'a> LookupSpan<'a> for EventRegistry {
    type Data = Data<'a>;

    fn span_data(&'a self, id: &Id) -> Option<Self::Data> {
        self.inner.span_data(id)
    }
}

impl Subscriber for EventRegistry {
    fn enabled(&self, metadata: &Metadata<'_>) -> bool {
        self.inner.enabled(metadata)
    }

    fn new_span(&self, span: &Attributes<'_>) -> Id {
        self.inner.new_span(span)
    }

    fn record(&self, span: &Id, values: &Record<'_>) {
        self.inner.record(span, values)
    }

    fn record_follows_from(&self, span: &Id, follows: &Id) {
        self.inner.record_follows_from(span, follows)
    }

    fn event(&self, event: &Event<'_>) {
        self.inner.event(event)
    }

    fn enter(&self, span: &Id) {
        self.inner.enter(span)
    }

    fn exit(&self, span: &Id) {
        self.inner.exit(span)
    }
}
