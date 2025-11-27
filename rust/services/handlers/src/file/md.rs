use std::path::Path;

use derive_more::{AsRef, Deref, DerefMut, From};
use serde::{Deserialize, Serialize};

use crate::file::{FileBase, FileTrait};

#[derive(Debug, Clone, Default, From, AsRef, Deref, DerefMut, Serialize, Deserialize)]
#[from(forward)]
#[as_ref(forward)]
pub struct Md {
    file: FileBase,
}

impl Md {
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self::make_new(file)
    }
}

impl FileTrait for Md {
    fn make_new(file: impl AsRef<Path>) -> Self {
        Self {
            file: FileBase::new_with_handler::<Self>(file),
        }
    }
    
    fn ext() -> &'static str {
        "md"
    }

    fn initialize_file(_: &mut std::fs::File) {}
}

impl From<&str> for Md {
    fn from(value: &str) -> Self {
        Self::new(value)
    }
}
