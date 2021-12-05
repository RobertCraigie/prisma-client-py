use pyo3::{create_exception, prelude::*};

mod engine;
mod error;
mod logger;
mod py_api;

pub(crate) type Result<T> = std::result::Result<T, error::ApiError>;
pub(crate) type Executor = Box<dyn query_core::QueryExecutor + Send + Sync>;

create_exception!(
    _prisma_query_engine,
    PrismaRustError,
    pyo3::exceptions::PyException
);
create_exception!(_prisma_query_engine, JsonError, PrismaRustError);
create_exception!(_prisma_query_engine, CrossbeamError, PrismaRustError);
create_exception!(_prisma_query_engine, NotConnectedError, PrismaRustError);
create_exception!(_prisma_query_engine, ConfigurationError, PrismaRustError);
create_exception!(_prisma_query_engine, AlreadyConnectedError, PrismaRustError);

#[pymodule]
fn _prisma_query_engine(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<py_api::PythonEngine>()?;

    // TODO: test all of these
    m.add("PrismaRustError", py.get_type::<PrismaRustError>())?;
    m.add("JsonError", py.get_type::<JsonError>())?;
    m.add("CrossbeamError", py.get_type::<CrossbeamError>())?;
    m.add("NotConnectedError", py.get_type::<NotConnectedError>())?;
    m.add("ConfigurationError", py.get_type::<ConfigurationError>())?;
    m.add(
        "AlreadyConnectedError",
        py.get_type::<AlreadyConnectedError>(),
    )?;

    Ok(())
}
