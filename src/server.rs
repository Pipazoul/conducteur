use crate::{docker, monitoring};
use std::time::Duration;
use tokio::time::sleep; 
use crate::utils;
use crate::types::{Node, Config}; // Importing the structs from types.rs
use crate::db::node; // Ensure unnecessary imports are removed in node.rs

pub async fn watch_node(node: Node, config: Config) {
    loop {
        println!("Watching node: {:?}", node.name);
        let _client = docker::connect(&node); // Use reference here to avoid moving node
        monitoring::usage(node.clone(), &_client).await; // Clone node here since it's reused in the loop
        node::update(&config.db, node.clone()); // Clone node here since it's reused in the loop

        sleep(Duration::from_secs(5)).await;
    }
}

pub async fn start(config_path: &str) {
    let config = utils::read_config(config_path).unwrap(); // Consider implementing error handling

    let mut handles = Vec::new();
    for node in &config.nodes {
        let config_clone = config.clone();
        println!("Foreach node: {:?}", node.name);
        let node_clone = node.clone(); // Clone the node to move into the async block
        let watch = tokio::spawn(async move {
            watch_node(node_clone, config_clone).await
        });
        handles.push(watch);
    }
    // Consider handling or awaiting the tasks stored in `handles`
    loop {
        sleep(Duration::from_secs(1)).await;
    }
}
