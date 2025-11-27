use std::{
    fs::create_dir_all,
    ops::Div,
    path::{Path, PathBuf},
};

use derive_more::{AsMut, AsRef, Deref, DerefMut, From, IntoIterator};
use serde::{Deserialize, Serialize};

use crate::file::{File, FileTrait, FileTypes, FsHandler};

#[derive(
    Debug, Default, From, IntoIterator, AsRef, AsMut, Deref, DerefMut, Serialize, Deserialize,
)]
#[from(forward)]
pub struct Dir {
    #[deref]
    #[deref_mut]
    #[as_ref(forward)]
    path: PathBuf,
    #[into_iterator(owned, ref, ref_mut)]
    #[from(skip)]
    pub files: Vec<FileTypes>,
}

impl Dir {
    /// Creates a new `Dir` instance from a given path.
    ///
    /// If the path already exists, it must be a directory. If it does not exist, it will be created recursively.
    ///
    /// # Panics
    ///
    /// If the path cannot be created, a panic will occur with the error message.
    pub fn new(dir: impl AsRef<Path>) -> Self {
        let dir = dir.as_ref().to_path_buf();

        if dir.exists() {
            assert!(dir.is_dir(), "{dir:?} is not a directory")
        } else {
            create_dir_all(&dir)
                .unwrap_or_else(|e| panic!("Failed to create directories for {dir:?}: {e}"));
        }

        Self {
            path: dir,
            files: vec![],
        }
    }

    pub fn add(&mut self, file: FileTypes) {
        self.files.push(file)
    }
}

impl From<&Path> for Dir {
    fn from(value: &Path) -> Self {
        Self::new(value)
    }
}

impl From<PathBuf> for Dir {
    fn from(value: PathBuf) -> Self {
        Self::new(value)
    }
}

impl From<&str> for Dir {
    fn from(value: &str) -> Self {
        Dir::new(value)
    }
}

impl<P: FileTrait> Div<P> for Dir {
    type Output = P;
    fn div(self, rhs: P) -> Self::Output {
        P::from(self.join(rhs))
    }
}

impl Div<Self> for Dir {
    type Output = Self;
    fn div(self, rhs: Dir) -> Self::Output {
        Self::new(self.join(rhs))
    }
}

impl Div<&str> for Dir {
    type Output = FsHandler<File>;
    fn div(self, rhs: &str) -> Self::Output {
        let new_path = self.path.join(rhs);
        if let Some(_) = new_path.extension() {
            FsHandler::File(File::new(self.join(rhs)))
        } else {
            FsHandler::Dir(Self::new(self.join(rhs)))
        }
    }
}
