use std::{fs, path::Path};

use derive_more::{AsRef, Deref, DerefMut, From};
use serde::{Deserialize, Serialize};

use crate::file::{FileBase, FileTrait};

#[derive(Debug, Clone, Default, From, AsRef, Deref, DerefMut, Serialize, Deserialize)]
#[from(forward)]
#[as_ref(forward)]
pub struct File {
    file: FileBase,
}

impl File {
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self::make_new(file)
    }
}

impl FileTrait for File {
    fn make_new(file: impl AsRef<Path>) -> Self {
        Self {
            file: FileBase::new_with_handler::<Self>(file),
        }
    }
    fn initialize_file(_: &mut fs::File) {}
    fn ext() -> &'static str {
        ""
    }
}

impl From<&str> for File {
    fn from(value: &str) -> Self {
        Self::new(value)
    }
}
