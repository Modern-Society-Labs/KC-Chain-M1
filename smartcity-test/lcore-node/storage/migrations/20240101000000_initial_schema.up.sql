-- Create the devices table
CREATE TABLE IF NOT EXISTS devices (
    id TEXT PRIMARY KEY NOT NULL,
    public_key TEXT NOT NULL,
    registration_date INTEGER NOT NULL
);

-- Create the data_submissions table
CREATE TABLE IF NOT EXISTS data_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    data BLOB NOT NULL,
    submission_date INTEGER NOT NULL,
    transaction_hash TEXT,
    FOREIGN KEY(device_id) REFERENCES devices(id)
); 