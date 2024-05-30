use serde_yml;
use std::{fs::File, io::Read};
use crate::types::Config;

pub fn read_config(file_path: &str) -> Result<Config, serde_yml::Error> {
    let mut file = File::open(file_path).unwrap();
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();
    return serde_yml::from_str(&contents);
}