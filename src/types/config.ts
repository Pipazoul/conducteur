import type { Role } from "./nodes";

export interface NodeConfig {
    name: string;
    role: Role;
    webuiPort?: number;
    auth?: {
        token: string;
    };
    weight?: number;
    socket?: string;
    host?: string;
    port?: number;
}

export interface Config {
    config: NodeConfig[];
}
