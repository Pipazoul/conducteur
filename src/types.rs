// types.rs
use serde::{Deserialize, Serialize};
use ormlite::model::*;

#[derive(Debug, Serialize, Deserialize)]
pub struct Config {
    pub nodes: Vec<Node>,
}

#[derive(Debug, Serialize, Deserialize)]
#[derive(Model, Debug)]
pub struct Node {
    pub id: i32,
    pub name: String,
    pub role: String,
    pub webui_port: Option<u16>,
    pub weight: Option<u8>,
    pub ip: Option<String>,
    pub rsa_key: Option<String>,
    pub jobs: Vec<Job>
}

#[derive(Debug, Serialize, Deserialize)]
#[derive(Model, Debug)]
pub struct Job {
    pub id: i32,
    pub name: String,
    pub node_id: i32,
    pub status: String,
    pub created_at: i64,
    pub updated_at: i64,
}

