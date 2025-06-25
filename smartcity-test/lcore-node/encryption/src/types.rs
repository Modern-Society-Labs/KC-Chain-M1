use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Plaintext(pub Vec<u8>);

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EncryptedData(pub Vec<u8>); 