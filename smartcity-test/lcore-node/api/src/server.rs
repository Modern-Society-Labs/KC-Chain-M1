use anyhow::Result;
use axum::{
    routing::{get, post},
    Router,
};
use std::net::SocketAddr;
use std::sync::Arc;
use std::time::Duration;
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use tracing::info;

use crate::{
    config::ApiConfig,
    handlers::{device_handler, status_handler},
    middleware::auth_middleware,
};

#[derive(Debug)]
pub struct Server {
    config: ApiConfig,
    storage: Arc<storage::sqlite::Connection>,
    encryption: Arc<encryption::DualEncryptionService>,
    kc_chain: Arc<kc_chain::Client>,
}

impl Server {
    pub fn new(
        config: ApiConfig,
        storage: Arc<storage::sqlite::Connection>,
        encryption: Arc<encryption::DualEncryptionService>,
        kc_chain: Arc<kc_chain::Client>,
    ) -> Self {
        Self {
            config,
            storage,
            encryption,
            kc_chain,
        }
    }

    pub async fn run(self) -> Result<()> {
        let cors = CorsLayer::new()
            .allow_origin(
                self.config
                    .cors_origins
                    .iter()
                    .map(|s| s.parse().unwrap())
                    .collect::<Vec<_>>(),
            )
            .allow_methods(tower_http::cors::Any)
            .allow_headers(tower_http::cors::Any);

        // Rate limiting disabled for MVP compile sanity

        let app = Router::new()
            .route("/status", get(status_handler::status))
            .merge(self.create_authenticated_router())
            .layer(TraceLayer::new_for_http())
            .layer(cors)
            .with_state(Arc::new(self.create_app_state()));

        let addr = SocketAddr::from(([0, 0, 0, 0], self.config.port));
        info!("API server listening on {}", addr);

        let listener = tokio::net::TcpListener::bind(addr).await?;
        axum::serve(listener, app.into_make_service_with_connect_info::<SocketAddr>()).await?;
        Ok(())
    }

    fn create_authenticated_router(&self) -> Router<Arc<AppState>> {
        Router::new()
            .route("/device/register", post(device_handler::register_device))
            .route("/device/data", post(device_handler::submit_data))
            .route_layer(axum::middleware::from_fn_with_state(
                self.create_app_state(),
                auth_middleware,
            ))
    }

    fn create_app_state(&self) -> AppState {
        AppState {
            storage: self.storage.clone(),
            encryption: self.encryption.clone(),
            kc_chain: self.kc_chain.clone(),
        }
    }
}

#[derive(Clone, Debug)]
pub struct AppState {
    pub storage: Arc<storage::sqlite::Connection>,
    pub encryption: Arc<encryption::DualEncryptionService>,
    pub kc_chain: Arc<kc_chain::Client>,
} 