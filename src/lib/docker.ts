// @deno-types="npm:@types/docker-modem"
import Modem from 'npm:docker-modem';

export async function connect(config: Modem.ConstructorOptions): Promise<Modem>{
    console.log("Connecting to Docker...");
    const modem = new Modem(config);
    return modem;
}


export default {
    connect
}