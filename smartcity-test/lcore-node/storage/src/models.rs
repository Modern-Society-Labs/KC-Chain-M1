use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct Device {
    pub id: String,
    pub public_key: String,
    pub registration_date: i64,
}

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct DataSubmission {
    pub id: i64,
    pub device_id: String,
    pub data: Vec<u8>,
    pub submission_date: i64,
    pub transaction_hash: Option<String>,
} 