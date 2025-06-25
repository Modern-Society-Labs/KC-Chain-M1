use crate::{
    error::EncryptionError,
    types::{EncryptedData},
};
use chacha20poly1305::{
    aead::{Aead, KeyInit, OsRng, AeadCore},
    ChaCha20Poly1305, Nonce,
};

#[derive(Debug)]
pub struct Stage2Encryptor {
    key: [u8; 32],
}

impl Stage2Encryptor {
    pub fn new(key: [u8; 32]) -> Self {
        Self { key }
    }

    pub fn encrypt(&self, data: &EncryptedData) -> Result<EncryptedData, EncryptionError> {
        let cipher = ChaCha20Poly1305::new_from_slice(&self.key).unwrap();
        let nonce = ChaCha20Poly1305::generate_nonce(&mut OsRng);
        let ciphertext = cipher
            .encrypt(&nonce, data.0.as_ref())
            .map_err(|e| EncryptionError::Stage2(e.to_string()))?;

        let mut encrypted_data = nonce.to_vec();
        encrypted_data.extend_from_slice(&ciphertext);

        Ok(EncryptedData(encrypted_data))
    }

    pub fn decrypt(&self, data: &EncryptedData) -> Result<EncryptedData, EncryptionError> {
        let cipher = ChaCha20Poly1305::new_from_slice(&self.key).unwrap();
        let (nonce_raw, ciphertext) = data.0.split_at(12);
        let nonce = Nonce::from_slice(nonce_raw);
        let plaintext = cipher
            .decrypt(nonce, ciphertext)
            .map_err(|e| EncryptionError::Stage2(e.to_string()))?;
        Ok(EncryptedData(plaintext))
    }
} 