use thiserror::Error;

#[derive(Error, Debug)]
pub enum EncryptionError {
    #[error("Failed to encrypt data")]
    EncryptionFailed,

    #[error("Failed to decrypt data")]
    DecryptionFailed,

    #[error("Invalid key format")]
    InvalidKey,

    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Stage 1 encryption failed: {0}")]
    Stage1(String),

    #[error("Stage 2 encryption failed: {0}")]
    Stage2(String),

    #[error("Invalid key length")]
    InvalidKeyLength,
} 