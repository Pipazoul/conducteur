export interface Node {
    ip: string;
    role?: Role;
    weight: number;
    bandwidth: {
        up?: number;
        down?: number;
    }
    jobs: [],
    specs: {
        cpu: number;
        ram: number;
        vram?: number;
        gpu?: number;
        storage: number;
    }
}

export enum Role {
    manager = "manager",
    worker = "worker"
}

export interface Job {
    id: string;
    name: string;
    status: "running" | "pending" | "complete" | "failed";
    image: string;
    ports: [];
    node: string;
    specs: {
        cpu: number;
        ram: number;
        vram?: number;
        gpu?: number;
        storage: number;
    }
    logs: string[];
}
