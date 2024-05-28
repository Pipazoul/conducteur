import type Dockerode from 'dockerode';
import Docker from 'dockerode';

export async function connect(config: Dockerode.DockerOptions): Promise<Modem>{
    console.log("Connecting to Docker...");
    const modem = new Docker(config);
    return modem;
}


export default {
    connect
}