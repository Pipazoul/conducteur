import YAML from 'npm:yaml'
import { parse } from "https://deno.land/std@0.98.0/encoding/yaml.ts";
import { exists } from "https://deno.land/std@0.98.0/fs/mod.ts";
import type { NodeConfig } from "../types/config.ts";
import { Role } from "../types/nodes.ts";
import docker from "./docker.ts";


export async function parseConfig(config: string): Promise<Array<NodeConfig>> {
    if (!await exists(config)) {
        console.error('Configuration file does not exist.');
        Deno.exit(1); // Exit the program with a status code of 1
    }
    try {
        const text = await Deno.readTextFile(config);
        const parsed = parse(text) as { config: Array<NodeConfig> };
        return parsed.config;
    }
    catch (e) {
        if (e instanceof Error) {
            console.error('Error parsing configuration file.');
            console.error(e.message);
        } else {
            console.error('Unknown error occurred.');
        }
        Deno.exit(1);
    }
}

export async function watchNode(node: NodeConfig){
    console.log("Watching node");
    console.log(node);
    let socket;
    if(node.socket) {
        socket = docker.connect({
            socketPath: node.socket
        });
    }
    if(node.host && node.port) {
        socket = docker.connect({
            host: node.host,
            port: node.port
        });
    }
    console.log("Connected to Docker");
    console.log(socket);
}



export async function start(configPath: string = "./config.yml"): Promise<string> {
    console.log("Starting server...");
    const config = await parseConfig(configPath);
    // for each config
    config.forEach(async (node) => {
        if(node.role == Role.manager) {
            console.log("Manager node detected");
        }
        if(node.role == Role.worker) {
            console.log("Worker node detected");
            // not awaiting this function because we want to run it in the background
            watchNode(node);
        }
    });


    return "Server started";
}

export default {
    start
}