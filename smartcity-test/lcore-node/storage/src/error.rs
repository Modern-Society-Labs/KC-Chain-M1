use thiserror::Error;

#[derive(Error, Debug)]
pub enum StorageError {
    #[error("Database query failed: {0}")]
    QueryError(#[from] sqlx::Error),

    #[error("Database migration failed: {0}")]
    MigrationFailed(#[from] sqlx::migrate::MigrateError),

    #[error("Record not found")]
    NotFound,
} 