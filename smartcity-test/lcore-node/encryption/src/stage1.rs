use crate::{
    error::EncryptionError,
    types::{EncryptedData, Plaintext},
};
use aes_gcm::{
    aead::{Aead, KeyInit, OsRng, AeadCore},
    Aes256Gcm, Nonce,
};

#[derive(Debug)]
pub struct Stage1Encryptor {
    key: [u8; 32],
}

impl Stage1Encryptor {
    pub fn new(key: [u8; 32]) -> Self {
        Self { key }
    }

    pub fn encrypt(&self, data: &Plaintext) -> Result<EncryptedData, EncryptionError> {
        let cipher = Aes256Gcm::new_from_slice(&self.key).unwrap();
        let nonce = Aes256Gcm::generate_nonce(&mut OsRng);
        let ciphertext = cipher
            .encrypt(&nonce, data.0.as_ref())
            .map_err(|e| EncryptionError::Stage1(e.to_string()))?;

        let mut encrypted_data = nonce.to_vec();
        encrypted_data.extend_from_slice(&ciphertext);

        Ok(EncryptedData(encrypted_data))
    }

    pub fn decrypt(&self, data: &EncryptedData) -> Result<Plaintext, EncryptionError> {
        let cipher = Aes256Gcm::new_from_slice(&self.key).unwrap();
        let (nonce_raw, ciphertext) = data.0.split_at(12);
        let nonce = Nonce::from_slice(nonce_raw);
        let plaintext = cipher
            .decrypt(nonce, ciphertext)
            .map_err(|e| EncryptionError::Stage1(e.to_string()))?;
        Ok(Plaintext(plaintext))
    }
} 