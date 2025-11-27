use std::{
    fmt::Debug,
    fs::{self, File, create_dir_all},
    path::{Path, PathBuf},
};

use derive_more::{AsRef, Deref, DerefMut, From};
use serde::{Deserialize, Serialize, de::DeserializeOwned};

#[derive(Debug, Clone, Default, From, AsRef, Serialize, Deserialize)]
#[as_ref(forward)]
pub struct FileBase {
    // TODO: With thousands of paths, central storage is preferable. Something like a mini filesystem. OPTIMIZATIONS BABE
    pub file: PathBuf,
}

impl FileBase {
    /// Creates a new FileHandler.
    ///
    /// If the file does not exist, it will be created. If the parent directories do not exist, they will be created.
    ///
    /// The file will be initialized according to the rules of the Handler type.
    ///
    /// # Panics
    ///
    /// Panics if the path is not a file or if the file does not have the correct extension.
    pub fn new_with_handler<H: FileTrait>(file: impl AsRef<Path>) -> Self {
        let file = file.as_ref().to_path_buf();

        if !H::ext().is_empty() {
            match file.extension() {
                Some(ext) => {
                    let ext = ext.to_str().expect("Extension should be a valid UTF-8");
                    assert_eq!(
                        ext,
                        H::ext(),
                        "Extension must be `{}` for file {file:?}, given: `{ext}`",
                        H::ext()
                    )
                }
                None => {
                    panic!(
                        "Extension must be `{}` for file {file:?}, no extension given",
                        H::ext()
                    )
                }
            }
        }

        if !file.exists() {
            if let Some(parent) = file.parent() {
                create_dir_all(parent).unwrap_or_else(|e| {
                    panic!("Failed to create parent directories for {file:?}: {e}")
                });
            }

            let mut f = File::create(&file)
                .unwrap_or_else(|e| panic!("Failed to create file {file:?}: {e}"));

            H::initialize_file(&mut f);
        }

        Self { file }
    }

    pub fn save(&self, data: impl AsRef<[u8]>) -> std::io::Result<()> {
        fs::write(&self.file, data).unwrap();
        Ok(())
    }

    pub fn load(&self) -> std::io::Result<String> {
        fs::read_to_string(&self.file)
    }
}

pub trait FileTrait:
    Debug
    + Clone
    + Default
    + From<PathBuf>
    + From<&'static str>
    + AsRef<Path>
    + std::ops::Deref<Target = FileBase>
    + std::ops::DerefMut
    + Serialize
    + DeserializeOwned
{
    fn make_new(file: impl AsRef<Path>) -> Self;
    fn initialize_file(file: &mut File);
    fn ext() -> &'static str;
}

#[derive(Debug, Clone, From, Deref, DerefMut)]
pub struct Temporary<H: FileTrait> {
    inner: H,
}

impl<H: FileTrait> Temporary<H> {
    pub fn new(handler: H) -> Self {
        Self { inner: handler }
    }
}

impl<T: FileTrait> Drop for Temporary<T> {
    fn drop(&mut self) {
        fs::remove_file(&self.file).unwrap();
        for dir in self.file.parent().into_iter().rev() {
            if fs::remove_dir(dir).is_err() {
                break;
            }
        }
    }
}
