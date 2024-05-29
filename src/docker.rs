use crate::types::Node;
use bollard::Docker;


pub fn connect( node: &Node) -> Docker {
    #[cfg(unix)]
    // if the node has an ip address
    if node.ip.is_some() {
        println!("SSH Connecting to node");
        return Docker::connect_with_unix_defaults().unwrap();
    }
    else {
        let docker = Docker::connect_with_local_defaults();
        print!("{:?}", docker);
        return docker.unwrap();
    }
}

