use anyhow::Result;
use serde::Deserialize;
use tracing::instrument;
use ethers::{
    middleware::SignerMiddleware,
    prelude::abigen,
    providers::{Http, Provider},
    signers::{LocalWallet, Signer},
    types::Address,
};
use std::sync::Arc;
use alloy_primitives::B256;
use hex::encode as hex_encode;

use crate::error::KCChainError;

abigen!(
    MVPIoTProcessor,
    "./MVPIoTProcessor.abi",
    event_derives(serde::Deserialize, serde::Serialize)
);

#[derive(Debug, Clone, Deserialize)]
pub struct ContractAddresses {
    pub mvp_processor: String,
    pub device_registry: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct KCChainConfig {
    pub rpc_url: String,
    pub ws_url: String,
    pub chain_id: u64,
    pub private_key: String,
    pub contracts: ContractAddresses,
}

#[derive(Debug, Clone)]
pub struct Client {
    processor: MVPIoTProcessor<SignerMiddleware<Provider<Http>, LocalWallet>>,
}

impl Client {
    #[instrument]
    pub async fn new(config: &KCChainConfig) -> Result<Self, KCChainError> {
        let provider = Provider::<Http>::try_from(config.rpc_url.as_str())
            .map_err(|e| KCChainError::Provider(e.to_string()))?;

        let wallet: LocalWallet = config
            .private_key
            .parse::<LocalWallet>()
            .map_err(|e| KCChainError::Initialization(format!("{e}")))?
            .with_chain_id(config.chain_id);

        let signer = Arc::new(SignerMiddleware::new(provider, wallet));

        let processor_addr: Address = config
            .contracts
            .mvp_processor
            .parse()
            .map_err(|e| KCChainError::Initialization(format!("{e}")))?;

        let processor = MVPIoTProcessor::new(processor_addr, signer.clone());

        Ok(Self {
            processor,
        })
    }

    #[instrument(skip(self, encrypted_data, proof_hash))]
    pub async fn submit_data(
        &self,
        task_id: B256,
        encrypted_data: Vec<u8>,
        proof_hash: B256,
    ) -> Result<String, KCChainError> {
        let task_arr: [u8; 32] = task_id.into();
        let proof_arr: [u8; 32] = proof_hash.into();

        let call = self
            .processor
            .submit_result(task_arr, encrypted_data.clone(), proof_arr)
            .gas(3_000_000u64);

        if let Some(calldata) = call.calldata() {
            println!("KC-Chain debug ‣ submit_result calldata: 0x{}", hex_encode(calldata));
        }

        let pending_tx = call
            .send()
            .await
            .map_err(|e| KCChainError::Submission(e.to_string()))?;

        let receipt = pending_tx
            .await
            .map_err(|e| KCChainError::Submission(e.to_string()))?
            .ok_or_else(|| KCChainError::Submission("Tx dropped from mempool".into()))?;

        Ok(format!("{:#x}", receipt.transaction_hash))
    }
} 