use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct ApiConfig {
    pub port: u16,
    pub cors_origins: Vec<String>,
    pub rate_limit_per_minute: u32,
} 