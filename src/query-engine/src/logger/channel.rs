use std::sync::Arc;

use super::visitor::JsonVisitor;
use serde_json::{Map, Value};
use tracing::{Event, Subscriber};
use tracing_subscriber::{layer::Context, registry::LookupSpan, EnvFilter, Layer};

#[derive(Clone)]
pub struct EventChannel {
    telemetry: bool,
    filter: Arc<EnvFilter>,
}

impl EventChannel {
    pub fn new(filter: EnvFilter, telemetry: bool) -> Self {
        Self {
            telemetry,
            filter: Arc::new(filter),
        }
    }
}

impl<S> Layer<S> for EventChannel
where
    S: Subscriber + for<'a> LookupSpan<'a>,
{
    fn on_event(&self, event: &Event<'_>, _: Context<'_, S>) {
        let mut object: Map<String, Value> = Map::with_capacity(5);

        object.insert(
            "level".to_string(),
            format!("{}", event.metadata().level()).into(),
        );

        let metadata = event.metadata();
        if let Some(module_path) = metadata.module_path() {
            object.insert("module_path".to_string(), module_path.into());
        }

        let mut visitor = JsonVisitor::new(&mut object);
        event.record(&mut visitor);

        let js_object = Value::Object(object);
        let json_str = serde_json::to_string(&js_object).unwrap();

        // TODO: proper logging
        println!("{}", json_str);
    }

    fn enabled(&self, metadata: &tracing::Metadata<'_>, ctx: Context<'_, S>) -> bool {
        self.telemetry || (!metadata.is_span() && self.filter.enabled(metadata, ctx))
    }
}
