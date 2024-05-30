// types.rs
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Config {
    pub nodes: Vec<Node>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Node {
    pub name: String,
    pub role: String,
    pub webui_port: Option<u16>,
    pub weight: Option<u8>,
    pub ip: Option<String>,
    pub rsa_key: Option<String>,
    pub jobs: Option<Vec<Job>>,
    pub db: Option<String>
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Job {
    pub id: i32,
    pub name: String,
    pub node_id: i32,
    pub status: String,
    pub created_at: i64,
    pub updated_at: i64,
}

