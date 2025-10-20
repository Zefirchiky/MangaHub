use std::{fs::{File}, io::Write, ops::Deref, path::{Path}};

use crate::file_handler::{FileHandler, Handler, TemporaryHandler};


pub struct JsonHandler {
    handler: FileHandler
}

impl JsonHandler {
    /// Creates a new JsonHandler for the given file.
    ///
    /// If the file does not exist, it will be created. If the parent directories do not exist, they will be created.
    ///
    /// # Panics
    ///
    /// Panics if the path exists but is not a file, or if the file does not have the correct extension.
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self {
            handler: FileHandler::new::<Self>(file)
        }
    }
}

impl Deref for JsonHandler {
    type Target = FileHandler;
    fn deref(&self) -> &Self::Target {
        &self.handler
    }
}

impl Handler for JsonHandler {
    fn initialize_file(file: &mut File) {
        file.write_all(b"{}")
            .expect("Failed to write initial JSON content");
    }

    fn ext() -> String {
        "json".to_string()
    }
}

impl TemporaryHandler for JsonHandler {}


#[cfg(test)]
mod json_handler_tests {
    use std::fs;

    use crate::{file_handler::Temporary, JsonHandler};

    static FILE_NAME_EXT: &str = "dis/init.json";
    static TEMP_FILE_NAME_EXT: &str = "dis/init_temp.json";
    static FILE_NAME: &str = "dis/init";
    static TEMP_FILE_NAME: &str = "dis/init_temp";

    #[test]
    fn init() {
        JsonHandler::new(FILE_NAME_EXT);
        assert!(fs::exists(FILE_NAME_EXT).unwrap_or(false), "File {FILE_NAME_EXT} was not created");
    }
    
    #[test]
    #[should_panic]
    fn init_wrong_ext() {
        JsonHandler::new(FILE_NAME);
    }
    
    #[test]
    fn init_temp() {
        {
            let _tis = Temporary::new(JsonHandler::new(TEMP_FILE_NAME_EXT));
            assert!(fs::exists(TEMP_FILE_NAME_EXT).unwrap_or(false), "File {TEMP_FILE_NAME_EXT} was not created");
        }
        assert!(!fs::exists(TEMP_FILE_NAME_EXT).unwrap_or(false), "File {TEMP_FILE_NAME_EXT} was not deleted");
    }
    
    #[test]
    #[should_panic]
    fn init_temp_wrong_ext() {
        Temporary::new(JsonHandler::new(TEMP_FILE_NAME));
    }
}