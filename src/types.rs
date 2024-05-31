// types.rs
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
#[derive(Clone)] // Implement the Clone trait for the Config struct
pub struct Config {
    pub db: String,
    pub nodes: Vec<Node>,
}

#[derive(Debug, Serialize, Deserialize)]
#[derive(Clone)] //
pub struct Database {
    pub nodes: Vec<Node>,
}

impl Default for Database {
    fn default() -> Self {
        Database {
            nodes: Vec::new(), // Initialize with an empty vector of nodes
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
#[derive(Clone)] //
pub struct Node {
    pub id: i32,
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
#[derive(Clone)] //
pub struct Job {
    pub id: i32,
    pub name: String,
    pub node_id: i32,
    pub status: String,
    pub created_at: i64,
    pub updated_at: i64,
}

