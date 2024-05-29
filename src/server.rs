use serde_yml;
use std::{fs::File, io::Read};
use crate::docker;
use std::time::Duration;
use tokio::{sync::watch, time::sleep}; 
use tokio::runtime::Runtime; // Import Tokio's runtime

use crate::types::{Config,Node}; // Importing the structs from types.rs


fn read_config(file_path: &str) -> Result<Config, serde_yml::Error> {
    let mut file = File::open(file_path).unwrap();
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();
    return serde_yml::from_str(&contents);
}

pub async fn watch_node(node: Node) {
    loop {
        println!("Watching node: {:?}", node.name);
        let client = docker::connect(&node);
        sleep(Duration::from_secs(5)).await;
    }
}


pub async fn start(config_path: &str) {
    let config = read_config(config_path).unwrap(); // Ideally handle errors more gracefully

    let mut handles = Vec::new();
    // async foreach node in config
    for node in config.nodes {
        println!("Foreach node: {:?}", node.name);
        let watch = tokio::spawn(watch_node(node));
        handles.push(watch);
    }

    let mut results = Vec::new();
    for watch in handles {
        results.push(watch.await);
    }
}