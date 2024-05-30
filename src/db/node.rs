use std::fs::File;
use std::io::{self, Write};
use serde_json;
use crate::types::{Database, Node};

// Adjust functions to return a more general error type
pub fn write_db_to_file(db: Database, file_path: &str) -> io::Result<()> {
    let mut file = File::create(file_path)?;
    let config_json = serde_json::to_string_pretty(&db).map_err(|e| io::Error::new(io::ErrorKind::Other, e))?;
    file.write_all(config_json.as_bytes())?;
    Ok(())
}

pub fn read_db_from_file(file_path: &str) -> io::Result<Database> {
    let file = match File::open(file_path) {
        Ok(file) => file,
        Err(_) => File::create(file_path)?,
    };
    if file.metadata()?.len() == 0 {
        // Assume Database can be instantiated without a new method
        return Ok(Database::default()); // Assuming Database implements Default
    }
    serde_json::from_reader(file).map_err(|e| io::Error::new(io::ErrorKind::Other, e))
}


pub fn create(db_path: &str, node: Node) {
    let mut db = read_db_from_file(db_path).unwrap();
    db.nodes.push(node);
    write_db_to_file(db, db_path).unwrap();
}