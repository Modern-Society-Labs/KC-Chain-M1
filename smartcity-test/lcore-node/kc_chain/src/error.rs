use thiserror::Error;

#[derive(Error, Debug)]
pub enum KCChainError {
    #[error("Initialization error: {0}")]
    Initialization(String),

    #[error("Transaction submission error: {0}")]
    Submission(String),

    #[error("Smart contract error: {0}")]
    Contract(String),

    #[error("Provider error: {0}")]
    Provider(String),
} 