use crate::types::Node;
use bollard::{container::{Config, CreateContainerOptions, ListContainersOptions, StartContainerOptions}, secret::ContainerConfig, Docker};
use std::collections::HashMap;


pub fn connect( node: &Node) -> Docker {
    #[cfg(unix)]
    // if the node has an ip address
    if node.ip.is_some() {
        println!("SSH Connecting to node");
        return Docker::connect_with_unix_defaults().unwrap();
    }
    else {
        let docker = Docker::connect_with_local_defaults();
        print!("{:?}", docker);
        return docker.unwrap();
    }
}


pub struct CustomConfig {
    pub name: String,
    pub image: String,
}

pub async fn create_container(
    docker: &Docker, 
    config: CustomConfig,
) -> Result<(), bollard::errors::Error> {

    let create_options = CreateContainerOptions {
        name: config.name,
        platform: Some("linux/amd64".to_string()),
    };

    let config = Config {
        image: Some(config.image),
        //cmd: config.cmd,
        //env: config.env,
        //exposed_ports: 
        //tty: Some(config.tty.unwrap_or(false)),
        ..Default::default()
    };

    let response = docker.create_container(Some(create_options), config).await;

    match response {
        Ok(container_info) => {
            println!("Container created with ID: {}", container_info.id);

            // Optionally start the container
            // No additional options required, hence passing None
            docker.start_container(&container_info.id, None::<StartContainerOptions<String>>).await?;

            Ok(())
        },
        Err(e) => {
            eprintln!("Failed to create container: {:?}", e);
            Err(e)
        }
    }
}

pub async fn does_container_exist(docker: &Docker, container_name: &str) -> Result<bool, bollard::errors::Error> {
    let mut filters = HashMap::new();
    filters.insert(String::from("name"), vec![container_name.to_string()]);  // Ensure the filter uses the correct type

    let options = Some(ListContainersOptions {
        all: true,
        limit: Some(1),
        filters,
        size: false,
        ..Default::default()
    });

    let containers = docker.list_containers(options).await?;

    for container in containers {
        // Check each container's name
        for name in &container.names {  // Explicitly iterate over names
            for n in name {
                if n == container_name {
                    return Ok(true);
                }
            }
        }
    }

    Ok(false)
}
