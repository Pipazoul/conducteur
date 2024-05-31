use std::fs::File;
use std::io::{self, Read, Write};
use serde_json;
use crate::types::{Database, Node};

// Adjust functions to handle errors more explicitly and use a more general error type if needed
pub fn write_db_to_file(db: &Database, file_path: &str) -> io::Result<()> {
    let config_json = serde_json::to_string_pretty(&db).map_err(|e| io::Error::new(io::ErrorKind::Other, e))?;
    let mut file = File::create(file_path)?;
    file.write_all(config_json.as_bytes())?;
    Ok(())
}

pub fn read_db_from_file(file_path: &str) -> io::Result<Database> {
    let mut file = File::open(file_path).or_else(|_| File::create(file_path))?;
    
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    if contents.is_empty() {
        // Return a new or default Database if the file is empty
        Ok(Database::default())
    } else {
        serde_json::from_str(&contents).map_err(|e| io::Error::new(io::ErrorKind::Other, e))
    }
}


pub fn update(db_path: &str, node: Node) -> io::Result<()> {
    let mut db = read_db_from_file(db_path)?;
    // update the node in the database or add it if it doesn't exist based on node.id
    let node_id = node.id;
    let node_index = db.nodes.iter().position(|n| n.id == node_id);
    match node_index {
        Some(index) => {
            db.nodes[index] = node;
        },
        None => {
            db.nodes.push(node);
        }
    }
    write_db_to_file(&db, db_path)
}

