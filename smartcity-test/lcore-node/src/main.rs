use anyhow::Result;
use clap::Parser;
use std::sync::Arc;
use tokio;
use tracing::{info, instrument};

mod config;
mod error;

use api::server::Server;
use config::Config;
use encryption::DualEncryptionService;
use kc_chain::Client as KCChainClient;
use storage::sqlite::Connection as DbConnection;

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(short, long, default_value = "config.toml")]
    config: String,
    
    #[arg(short, long)]
    verbose: bool,
}

#[tokio::main]
#[instrument]
async fn main() -> Result<()> {
    let args = Args::parse();
    
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_max_level(if args.verbose { tracing::Level::DEBUG } else { tracing::Level::INFO })
        .with_env_filter(tracing_subscriber::filter::EnvFilter::from_default_env())
        .init();
    
    // Load configuration
    let config = Config::from_file(&args.config)?;
    info!("Loaded configuration from {}", args.config);
    
    // Initialize services
    let storage = Arc::new(DbConnection::new(&config.storage.database_url).await?);
    storage.run_migrations().await?;
    info!("Database migrations completed");

    let encryption_config = encryption::service::EncryptionConfig {
        key_rotation_hours: config.encryption.key_rotation_hours,
    };
    let encryption = Arc::new(DualEncryptionService::new(&encryption_config)?);

    let kc_chain_config = kc_chain::client::KCChainConfig {
        rpc_url: config.kc_chain.rpc_url,
        ws_url: config.kc_chain.ws_url,
        chain_id: config.kc_chain.chain_id,
        private_key: config.kc_chain.private_key,
        contracts: kc_chain::client::ContractAddresses {
            mvp_processor: config.kc_chain.contracts.mvp_processor,
            device_registry: config.kc_chain.contracts.device_registry,
        },
    };
    let kc_chain = Arc::new(KCChainClient::new(&kc_chain_config).await?);

    // Start API server
    let api_config = api::config::ApiConfig {
        port: config.api.port,
        cors_origins: config.api.cors_origins,
        rate_limit_per_minute: config.api.rate_limit_per_minute,
    };
    let api_server = Server::new(api_config, storage.clone(), encryption.clone(), kc_chain.clone());

    info!("Starting lcore-node MVP");
    api_server.run().await?;
    
    Ok(())
} 