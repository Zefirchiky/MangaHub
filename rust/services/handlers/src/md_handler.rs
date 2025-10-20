use std::{fs::{self, File}, ops::Deref, path::{Path}};

use crate::file_handler::{FileHandler, Handler};


pub struct MdHandler {
    handler: FileHandler
}

impl MdHandler {
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self {
            handler: FileHandler::new::<Self>(file)
        }
    }
}

impl Deref for MdHandler {
    type Target = FileHandler;
    fn deref(&self) -> &Self::Target {
        &self.handler
    }
}

impl Handler for MdHandler {
    fn initialize_file(_: &mut File) {}

    fn ext() -> String {
        "md".to_string()
    }
}


pub struct TemporaryMdHandler(MdHandler);

impl TemporaryMdHandler {
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self(MdHandler::new(file))
    }
}

impl Deref for TemporaryMdHandler {
    type Target = MdHandler;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl Drop for TemporaryMdHandler {
    fn drop(&mut self) {
        fs::remove_file(self.path()).unwrap();
        for dir in self.path().parent().into_iter().rev() {
            if fs::remove_dir(dir).is_err() {
                break
            }
        }
    }
}


#[cfg(test)]
mod md_handler_tests {
    use crate::{MdHandler, TemporaryMdHandler};

    #[test]
    fn init() {
        MdHandler::new("dis/pls.md");
    }

    #[test]
    #[should_panic]
    fn init_wrong_ext() {
        MdHandler::new("dis/pls");
    }
    
    #[test]
    fn init_temp() {
        TemporaryMdHandler::new("dis/pls.md");
    }
    
    #[test]
    #[should_panic]
    fn init_temp_wrong_ext() {
        TemporaryMdHandler::new("dis/pls");
    }
}