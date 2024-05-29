use clap::{Arg, Command};
use std::process;

// Assuming you have a module named `server` with a function `start`
mod server {
    pub async fn start(config: Option<String>) {
        // Dummy implementation
        println!("Starting server with config: {:?}", config);
    }
}

#[tokio::main] // Use tokio as the async runtime
fn main() {
    let matches = Command::new("conducteur")
        .version("0.0.1")
        .author("Your Name <your_email@example.com>")
        .about("A simple docker orchestration tool")
        .subcommand(
            Command::new("start")
                .about("🚈 Start server")
                .arg(Arg::new("config")
                    .long("config")
                    .help("Configuration file"))
                .action(|args| {
                    let config = args.get_one::<String>("config").cloned();
                    async move {
                        server::start(config).await;
                    }
                }),
        )
        .subcommand(
            Command::new("add-node")
                .about("🚃 Add a new node")
                .arg(Arg::new("name")
                    .help("Node name")
                    .required(true)
                    .index(1))
                .arg(Arg::new("url")
                    .help("URL of the node")
                    .required(true)
                    .index(2))
                .arg(Arg::new("token")
                    .help("Access token for the node")
                    .required(true)
                    .index(3))
                .action(|args| {
                    let name = args.get_one::<String>("name").expect("required");
                    let url = args.get_one::<String>("url").expect("required");
                    let token = args.get_one::<String>("token").expect("required");
                    println!("Adding node {} with url {} and token {}", name, url, token);
                }),
        )
        .try_get_matches();

    match matches {
        Ok(matches) => {
            if let Some(ref matches) = matches.subcommand_matches("start") {
                let config = matches.get_one::<String>("config").cloned();
                server::start(config).await;
            } else if let Some(ref matches) = matches.subcommand_matches("add-node") {
                let name = matches.get_one::<String>("name").unwrap();
                let url = matches.get_one::<String>("url").unwrap();
                let token = matches.get_one::<String>("token").unwrap();
                println!("Adding node {} with url {} and token {}", name, url, token);
            }
        }
        Err(error) => {
            eprintln!("{}", error);
            process::exit(1);
        }
    }
}
