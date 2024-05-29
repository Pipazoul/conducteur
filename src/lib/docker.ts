// @deno-types="npm:@types/dockerode"
import Docker from 'npm:dockerode';

export function connect(config: Docker.DockerOptions): Docker {
    const docker = new Docker(config);
    return docker;
}

export function listContainers(docker: Docker): Promise<Docker.ContainerInfo[]> {
    console.log("Listing containers");
    docker.listContainers()
    // return new Promise((resolve) => {
    //     docker.listContainers((err, containers) => {
    //         if(err) {
    //             console.error(err);
    //             resolve([]);
    //         }
    //         resolve(containers);
    //     });
    // });
}


export default {
    connect,
    listContainers
}