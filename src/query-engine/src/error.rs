use datamodel::diagnostics::Diagnostics;
use query_connector::error::ConnectorError;
use query_core::CoreError;
use std::fmt::Write;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ApiError {
    #[error("{}", _0)]
    Conversion(Diagnostics, String),

    #[error("{}", _0)]
    Configuration(String),

    #[error("{}", _0)]
    Core(CoreError),

    #[error("{}", _0)]
    Connector(ConnectorError),

    #[error("Can't modify an already connected engine.")]
    AlreadyConnected,

    #[error("Engine is not yet connected.")]
    NotConnected,

    #[error("{}", _0)]
    CrossbeamError(String),

    #[error("{}", _0)]
    JsonDecode(String),
}

impl From<ApiError> for user_facing_errors::Error {
    fn from(err: ApiError) -> Self {
        use std::fmt::Write as _;

        match err {
            ApiError::Connector(ConnectorError {
                user_facing_error: Some(err),
                ..
            }) => err.into(),
            ApiError::Conversion(errors, dml_string) => {
                let mut full_error = errors.to_pretty_string("schema.prisma", &dml_string);
                write!(
                    full_error,
                    "\nValidation Error Count: {}",
                    errors.errors().len()
                )
                .unwrap();

                user_facing_errors::Error::from(user_facing_errors::KnownError::new(
                    user_facing_errors::common::SchemaParserError { full_error },
                ))
            }
            ApiError::Core(error) => user_facing_errors::Error::from(error),
            other => {
                user_facing_errors::Error::new_non_panic_with_current_backtrace(other.to_string())
            }
        }
    }
}

impl ApiError {
    pub fn conversion(diagnostics: Diagnostics, dml: impl ToString) -> Self {
        Self::Conversion(diagnostics, dml.to_string())
    }

    pub fn configuration(msg: impl ToString) -> Self {
        Self::Configuration(msg.to_string())
    }
}

impl From<CoreError> for ApiError {
    fn from(e: CoreError) -> Self {
        match e {
            CoreError::ConfigurationError(message) => Self::Configuration(message),
            core_error => Self::Core(core_error),
        }
    }
}

impl From<ConnectorError> for ApiError {
    fn from(e: ConnectorError) -> Self {
        Self::Connector(e)
    }
}

impl From<url::ParseError> for ApiError {
    fn from(e: url::ParseError) -> Self {
        Self::configuration(format!("Error parsing connection string: {}", e))
    }
}

impl From<connection_string::Error> for ApiError {
    fn from(e: connection_string::Error) -> Self {
        Self::configuration(format!("Error parsing connection string: {}", e))
    }
}

impl From<serde_json::Error> for ApiError {
    fn from(e: serde_json::Error) -> Self {
        Self::JsonDecode(format!("{}", e))
    }
}

impl From<crossbeam_channel::RecvTimeoutError> for ApiError {
    fn from(e: crossbeam_channel::RecvTimeoutError) -> Self {
        match e {
            crossbeam_channel::RecvTimeoutError::Timeout => {
                Self::CrossbeamError("Channel timed out".to_string())
            }
            crossbeam_channel::RecvTimeoutError::Disconnected => {
                Self::CrossbeamError("Channel disconnected".to_string())
            }
        }
    }
}

impl From<crossbeam_channel::RecvError> for ApiError {
    fn from(e: crossbeam_channel::RecvError) -> Self {
        Self::CrossbeamError(format!("{}", e))
    }
}

impl From<ApiError> for pyo3::PyErr {
    fn from(e: ApiError) -> Self {
        match e {
            ApiError::Conversion(errors, dml_string) => {
                let mut full_error = errors.to_pretty_string("schema.prisma", &dml_string);
                write!(
                    full_error,
                    "\nValidation Error Count: {}",
                    errors.errors().len()
                )
                .unwrap();

                // it makes more sense to me for the user facing error to be a ConfigurationError
                // rather than a ConversionError
                crate::ConfigurationError::new_err(full_error)
            }
            // TODO: more verbose errors
            ApiError::Core(error) => {
                let user_facing = user_facing_errors::Error::from(error);
                let message = serde_json::to_string(&user_facing).unwrap();
                crate::PrismaRustError::new_err(message)
            }
            ApiError::Connector(error) => {
                let message = match error.user_facing_error {
                    Some(error) => serde_json::to_string(&error).unwrap(),
                    None => "Unkown connector error".to_string(),
                };
                crate::PrismaRustError::new_err(message)
            }
            ApiError::Configuration(message) => crate::ConfigurationError::new_err(message),
            ApiError::NotConnected => crate::NotConnectedError::new_err(e.to_string()),
            ApiError::AlreadyConnected => crate::AlreadyConnectedError::new_err(e.to_string()),
            ApiError::JsonDecode(data) => crate::JsonError::new_err(data),
            ApiError::CrossbeamError(msg) => crate::CrossbeamError::new_err(msg),
        }
    }
}
