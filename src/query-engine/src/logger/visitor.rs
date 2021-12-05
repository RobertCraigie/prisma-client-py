use serde_json::{Map, Value};
use std::fmt;
use tracing::field::{Field, Visit};

pub struct JsonVisitor<'a> {
    object: &'a mut Map<String, Value>,
}

impl<'a> JsonVisitor<'a> {
    pub fn new(object: &'a mut Map<String, Value>) -> Self {
        Self { object }
    }
}

impl<'a> Visit for JsonVisitor<'a> {
    fn record_debug(&mut self, field: &Field, value: &dyn fmt::Debug) {
        self.object
            .insert(field.name().to_string(), format!("{:?}", value).into());
    }

    fn record_i64(&mut self, field: &Field, value: i64) {
        self.object
            .insert(field.name().to_string(), format!("{}", value).into());
    }

    fn record_u64(&mut self, field: &Field, value: u64) {
        self.object
            .insert(field.name().to_string(), format!("{}", value).into());
    }

    fn record_bool(&mut self, field: &Field, value: bool) {
        self.object
            .insert(field.name().to_string(), format!("{}", value).into());
    }

    fn record_str(&mut self, field: &Field, value: &str) {
        self.object.insert(field.name().to_string(), value.to_string().into());
    }
}
