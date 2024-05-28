import { PrismaClient } from "@prisma/client";
import YAML from 'yaml'
import type { NodeConfig } from "../types/config";
import { Role } from "../types/nodes";
//import docker from "./docker";

const prisma = new PrismaClient();

export async function parseConfig(config: string): Promise<Array<NodeConfig>> {
    const file = Bun.file(config);
    if (! await file.exists()) {
        console.error('Configuration file does not exist.');
        process.exit(1); // Exit the program with a status code of 1
    }
    try {
        const parsed = YAML.parse(await file.text());
        return parsed.config
    }
    catch (e) {
        if (e instanceof YAML.YAMLError) {
            console.error('Error parsing configuration file.');
            console.error(e.message);
        }
        console.error('Error parsing configuration file.');
        console.error();
        process.exit(1);
    }

}

export async function watchNode(node: NodeConfig){
    console.log("Watching node");
    let socket;
    // if(node.socket) {
    //     socket = docker.connect({
    //         socketPath: node.socket
    //     });
    // }
    // if(node.host && node.port) {
    //     socket = docker.connect({
    //         host: node.host,
    //         port: node.port
    //     });
    // }
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