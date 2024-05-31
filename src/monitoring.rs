use bollard::Docker;

use crate::{docker::{create_container, does_container_exist, CustomConfig}, types::Node};


pub async fn usage(node: Node, client: &Docker) {
    println!("Node usage: {:?}", node.name);
    // verify if container exists
    let exists = does_container_exist(client, "stats").await.unwrap();
    if exists {
        println!("Container exists: {:?}", exists);
    }
    else {
        println!("Container does not exist: {:?}", exists);
        let config= CustomConfig {
            name: "stats".to_string(),
            image: "alpine:latest".to_string(), // Fix: Wrap the string literal with Some() to convert it into an Option<String>.
        };
        let response = create_container(client, config).await.unwrap();
        println!("Container created: {:?}", response)
    }
}