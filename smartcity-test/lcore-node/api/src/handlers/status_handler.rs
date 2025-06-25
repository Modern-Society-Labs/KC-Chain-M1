use axum::Json;
use serde::Serialize;
use tracing::instrument;

#[derive(Serialize)]
pub struct StatusResponse {
    status: String,
    version: String,
}

#[instrument]
pub async fn status() -> Json<StatusResponse> {
    Json(StatusResponse {
        status: "ok".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
    })
} 