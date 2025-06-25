use thiserror::Error;

#[derive(Error, Debug)]
pub enum DeviceError {
    #[error("Device with ID {0} already registered")]
    AlreadyExists(String),

    #[error("Device not found")]
    NotFound,

    #[error("Invalid public key")]
    InvalidPublicKey,

    #[error("Storage error: {0}")]
    Storage(#[from] storage::error::StorageError),
} 