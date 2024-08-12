# Orchestre 

Replicate for Homelabs

Orchrestre is a small cog docker container Orchrestratrator



## Features
- Multiple Nodes : You can multiple GPU host Orchrestre will load balance requests
- Scoped Token Management
- Web Dashboard
- Javascript sdk
- Co2 Monitoring



## What is Cog  ?
Cog is an API wrapper for machine learning models, its has been created and is used by Replicate for inference
Conducteur uses cog for inference



## Scoped Token Management
Scoped tokens allow you to restrict what a token can do. You can choose to allow prediction on specific docker images per usage

Observability:
Each token can be monitored in terms of co2 consumption / preductions duration / etc.


## Web Dashboard
We provide a web dashboard to

- Monitor Predictions
Get a real time view on running predictions and last 24 hours predictions.


- Monitor Nodes availability and usage
See if a Node is available and how much it's being use by running predictions

- Monitor Token usage
Get an summary of how much co2 is being used by each token for how long and on wich docker image.

- TODO Manage Tokens
Create, delete, update tokens and their scopes.

## Multiple Nodes
Orchestre allows you to run multiple nodes (A node is a physical of virtual machine with a GPU). This feature enables high throughput in the event of heavy load.


## Requirements
- A GPU Card (At least a RTX 3090 is highly recommended a lot of the cog container need at least 24 GB of VRAM)
- Docker installed on your machine
- 1To of SSD storage (Machine learnign Container are quite large and will require significant space)



## Roadmap

- CPU Inference (Already possible but only on GPU machine and only one after another)
