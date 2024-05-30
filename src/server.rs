
use crate::docker;
use std::time::Duration;
use tokio::time::sleep; 
use crate::utils;
use crate::types::Node; // Importing the structs from types.rs
use crate::db::node; // Importing the create function from db/node.rs


pub async fn watch_node(node: Node) {
    loop {
        println!("Watching node: {:?}", node.name);
        let client = docker::connect(&node);
        node::create();
        sleep(Duration::from_secs(5)).await;
    }
}


pub async fn start(config_path: &str) {
    let config = utils::read_config(config_path).unwrap(); // Ideally handle errors more gracefully

    let mut handles = Vec::new();
    // async foreach node in config
    for node in config.nodes {
        println!("Foreach node: {:?}", node.name);
        let watch = tokio::spawn(watch_node(node));
        handles.push(watch);
    }
    // loop forever
    loop {
        sleep(Duration::from_secs(1)).await;
    }
}