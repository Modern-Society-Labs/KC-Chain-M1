use anyhow::Result;
use sqlx::sqlite::{SqliteConnectOptions, SqlitePool};
use std::str::FromStr;
use tracing::instrument;

#[derive(Clone, Debug)]
pub struct Connection {
    pool: SqlitePool,
}

impl Connection {
    #[instrument]
    pub async fn new(database_url: &str) -> Result<Self> {
        let options = SqliteConnectOptions::from_str(database_url)?
            .create_if_missing(true);
        let pool = SqlitePool::connect_with(options).await?;
        Ok(Self { pool })
    }

    pub async fn run_migrations(&self) -> Result<()> {
        sqlx::migrate!("./migrations").run(&self.pool).await?;
        Ok(())
    }

    #[instrument(skip(self))]
    pub async fn register_device(&self, device_id: &str, public_key: &str) -> Result<()> {
        let res = sqlx::query("INSERT INTO devices (id, public_key, registration_date) VALUES (?, ?, strftime('%s','now'))")
            .bind(device_id)
            .bind(public_key)
            .execute(&self.pool)
            .await;

        match res {
            Ok(_) => Ok(()),
            Err(sqlx::Error::Database(db_err)) => {
                // Ignore duplicate primary key errors (already registered)
                if db_err.message().contains("UNIQUE constraint failed") {
        Ok(())
                } else {
                    Err(sqlx::Error::Database(db_err).into())
                }
            }
            Err(e) => Err(e.into()),
        }
    }

    #[instrument(skip(self, encrypted_data))]
    pub async fn store_encrypted_data(&self, device_id: &str, encrypted_data: &[u8]) -> Result<()> {
        let res = sqlx::query("INSERT INTO data_submissions (device_id, data, submission_date) VALUES (?, ?, strftime('%s','now'))")
            .bind(device_id)
            .bind(encrypted_data)
            .execute(&self.pool)
            .await;

        match res {
            Ok(_) => Ok(()),
            Err(sqlx::Error::Database(db_err)) => {
                if db_err.message().contains("FOREIGN KEY constraint failed") {
                    // Device not yet in devices table; treat as non-fatal for MVP
        Ok(())
                } else {
                    Err(sqlx::Error::Database(db_err).into())
                }
            }
            Err(e) => Err(e.into()),
        }
    }

    // Placeholder for a query method
    // pub async fn get_device(&self, device_id: &str) -> Result<Option<Device>, sqlx::Error> {
    //     // ... query logic ...
    // }
} 