use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Deserialize, Serialize)]
pub struct Config {
    pub api: ApiConfig,
    pub encryption: EncryptionConfig,
    pub storage: StorageConfig,
    pub kc_chain: KCChainConfig,
    pub risc_zero: RiscZeroConfig,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct ApiConfig {
    pub host: String,
    pub port: u16,
    pub cors_origins: Vec<String>,
    pub rate_limit_per_minute: u32,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct EncryptionConfig {
    pub key_rotation_hours: u64,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct StorageConfig {
    pub database_url: String,
    pub max_connections: u32,
    pub query_cache_ttl_minutes: u64,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct KCChainConfig {
    pub rpc_url: String,
    pub ws_url: String,
    pub chain_id: u64,
    pub private_key: String,
    pub contracts: ContractAddresses,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct ContractAddresses {
    pub mvp_processor: String,
    pub device_registry: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct RiscZeroConfig {
    pub dev_mode: bool,
    pub bonsai_api_key: Option<String>,
    pub bonsai_api_url: Option<String>,
}

impl Config {
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self, config::ConfigError> {
        let settings = config::Config::builder()
            .add_source(config::File::with_name(path.as_ref().to_str().unwrap()))
            .add_source(config::Environment::with_prefix("LCORE"))
            .build()?;
        
        settings.try_deserialize()
    }
} 