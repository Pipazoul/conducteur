use clap::{Parser, Subcommand};
mod server;
mod types; 
mod docker;
mod db;
mod utils;

/// Simple program to greet a person or start a service with a config file
#[derive(Parser, Debug)]
#[command(version = "0.1.0", about = "A simple docker orchestration tool", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {

    /// 🚈 Start server
    Start {
        /// Configuration file path
        #[arg(short, long)]
        config: String,
    },
}

#[tokio::main]
async fn main() {
    println!("################### 🚇 Conducteur v0.1.0 ###################");
    print!("\n");

    let cli = Cli::parse();
    match &cli.command {
        Commands::Start { config } => {
            // Add your logic here to handle the starting of the service
            server::start(config).await;
        }
    }
}
