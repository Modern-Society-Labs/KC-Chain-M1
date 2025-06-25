use axum::{extract::State, http::StatusCode, Json};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::instrument;
use sha2::{Digest, Sha256};
use alloy_primitives::B256;

use crate::server::AppState;

#[derive(Debug, Deserialize)]
pub struct RegisterDeviceRequest {
    pub device_id: String,
    pub public_key: String,
}

#[derive(Serialize)]
pub struct RegisterDeviceResponse {
    pub success: bool,
    pub message: String,
}

#[instrument(skip(state, req))]
pub async fn register_device(
    State(state): State<Arc<AppState>>,
    Json(req): Json<RegisterDeviceRequest>,
) -> (StatusCode, Json<RegisterDeviceResponse>) {
    let result = state
        .storage
        .register_device(&req.device_id, &req.public_key)
        .await;

    match result {
        Ok(_) => (
            StatusCode::CREATED,
            Json(RegisterDeviceResponse {
                success: true,
                message: "Device registered successfully".to_string(),
            }),
        ),
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(RegisterDeviceResponse {
                success: false,
                message: format!("Failed to register device: {}", e),
            }),
        ),
    }
}

#[derive(Debug, Deserialize)]
pub struct SubmitDataRequest {
    pub device_id: String,
    pub data: String,
}

#[derive(Serialize)]
pub struct SubmitDataResponse {
    pub success: bool,
    pub message: String,
}

#[instrument(skip(state, req))]
pub async fn submit_data(
    State(state): State<Arc<AppState>>,
    Json(req): Json<SubmitDataRequest>,
) -> (StatusCode, Json<SubmitDataResponse>) {
    let data_bytes = req.data.as_bytes().to_vec();

    let plaintext = encryption::types::Plaintext(data_bytes);

    let encrypted_data = match state.encryption.encrypt(plaintext) {
        Ok(data) => data,
        Err(e) => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(SubmitDataResponse {
                    success: false,
                    message: format!("Encryption failed: {}", e),
                }),
            );
        }
    };

    // Persist encrypted data locally first
    if let Err(e) = state
        .storage
        .store_encrypted_data(&req.device_id, &encrypted_data.0)
        .await
    {
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(SubmitDataResponse {
                success: false,
                message: format!("Failed to store data: {}", e),
            }),
        );
    }

    // For the MVP, we'll use a SHA-256 hash of the encrypted data as the task ID.
    // In a production system, this would be a more robust, unique identifier.
    let task_id: B256 = B256::from_slice(&Sha256::digest(&encrypted_data.0));

    // Similarly, we'll use a SHA-256 hash as the proof hash for the MVP.
    let proof_hash: B256 = B256::from_slice(&Sha256::digest(&encrypted_data.0));

    // Attempt to dispatch the encrypted blob to KC-Chain (non-blocking; errors logged but do not fail request)
    let tx_result = state
        .kc_chain
        .submit_data(task_id, encrypted_data.0, proof_hash)
        .await;

    match tx_result {
        Ok(tx_hash) => (
            StatusCode::OK,
            Json(SubmitDataResponse {
                success: true,
                message: format!("Data submitted; tx {}", tx_hash),
            }),
        ),
        Err(e) => (
            StatusCode::OK, // still 200: local persistence succeeded
            Json(SubmitDataResponse {
                success: true,
                message: format!("Data stored locally; KC-Chain dispatch failed: {}", e),
            }),
        ),
    }
} 