use anyhow::Result;
use serde::Deserialize;
use tracing::instrument;

use crate::{
    error::EncryptionError,
    stage1::Stage1Encryptor,
    stage2::Stage2Encryptor,
    types::{EncryptedData, Plaintext},
};

#[derive(Debug, Clone, Deserialize)]
pub struct EncryptionConfig {
    pub key_rotation_hours: u64,
}

#[derive(Debug)]
pub struct DualEncryptionService {
    stage1: Stage1Encryptor,
    stage2: Stage2Encryptor,
}

impl DualEncryptionService {
    #[instrument]
    pub fn new(_config: &EncryptionConfig) -> Result<Self> {
        // FIXME: In a production environment, keys should be loaded securely,
        // for example, from a secure vault or an environment variable.
        // For the MVP, we are using fixed, hardcoded keys.
        let stage1_key = [0u8; 32];
        let stage2_key = [1u8; 32];

        let stage1 = Stage1Encryptor::new(stage1_key);
        let stage2 = Stage2Encryptor::new(stage2_key);
        Ok(Self { stage1, stage2 })
    }

    #[instrument(skip(plaintext))]
    pub fn encrypt(&self, plaintext: Plaintext) -> Result<EncryptedData, EncryptionError> {
        // The two-stage encryption process
        let stage1_encrypted = self.stage1.encrypt(&plaintext)?;
        let stage2_encrypted = self.stage2.encrypt(&stage1_encrypted)?;
        Ok(stage2_encrypted)
    }

    #[instrument(skip(data))]
    pub fn decrypt(&self, data: EncryptedData) -> Result<Plaintext, EncryptionError> {
        // The two-stage decryption process
        let stage2_decrypted = self.stage2.decrypt(&data)?;
        let stage1_decrypted = self.stage1.decrypt(&stage2_decrypted)?;
        Ok(stage1_decrypted)
    }
} 