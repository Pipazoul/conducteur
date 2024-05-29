use clap::{Parser, Subcommand};
mod lib;

/// Simple program to greet a person or start a service with a config file
#[derive(Parser, Debug)]
#[command(version = "0.1.0", about = "A simple docker orchestration tool", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {

    /// Start the service with configuration
    Start {
        /// Configuration file path
        #[arg(short, long)]
        config: String,
    },
}

fn main() {
    println!("################### 🚇 Conducteur v0.1.0 ###################");
    print!("\n");

    let cli = Cli::parse();
    match &cli.command {
        Commands::Start { config } => {
            // Add your logic here to handle the starting of the service
        }
    }
}
