use std::{fmt::Debug, fs::{self, create_dir_all, File}, ops::Deref, path::{Path, PathBuf}};

use serde::{de::DeserializeOwned, Deserialize, Serialize};

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct FileHandler {    // TODO: With thousands of paths, central storage is preferable. Something like a mini filesystem. OPTIMIZATIONS BABE
    file: PathBuf
}

impl FileHandler {
    /// Creates a new FileHandler.
    ///
    /// If the file does not exist, it will be created. If the parent directories do not exist, they will be created.
    /// 
    /// The file will be initialized according to the rules of the Handler type.
    /// 
    /// # Panics
    /// 
    /// Panics if the path is not a file or if the file does not have the correct extension.
    pub fn new<H: Handler>(file: impl AsRef<Path>) -> Self {
        let file = file.as_ref().to_path_buf();

        assert!(!file.is_dir(), "Path must be a file, not a directory: {file:?}");
        let extension = match file.extension() {
            Some(ext) => ext.to_str().unwrap(),
            None => ""
        };
        assert!(extension == H::ext(), "File {file:?} must have '{}' extension", H::ext());

        if let Some(parent) = file.parent() {
            create_dir_all(parent)
                .unwrap_or_else(|e| panic!("Failed to create parent directories for {file:?}: {e}"));
        }


        let mut f = File::create(&file)
            .unwrap_or_else(|e| panic!("Failed to create file {file:?}: {e}"));

        H::initialize_file(&mut f);

        Self {
            file
        }
    }

    // TODO: Might be better, not sure
    // pub fn with_handler<H: Handler>(file: impl AsRef<Path>) -> Self {
    //     Self::new(file, |f| H::initialize_file(f))
    // }

    pub fn path(&self) -> &Path {
        &self.file
    }

    pub fn save<H: Handler>(&self, model: &impl Serialize) -> Result<(), serde_json::Error> {
        let res = H::to_string(model)?;
        fs::write(&self.file, res).unwrap();
        Ok(())
    }

    pub fn load<T: DeserializeOwned, H: Handler>(&self) -> Result<T, serde_json::Error> {
        let res = fs::read_to_string(&self.file).unwrap();
        H::from_string(&res)
    }
}

pub trait Handler: Debug + Default + Deref<Target = FileHandler> {
    fn initialize_file(file: &mut File);
    fn ext() -> String;
    fn to_string(model: &impl Serialize) -> Result<String, serde_json::Error>;
    fn from_string<T: DeserializeOwned>(s: &str) -> Result<T, serde_json::Error>;
}

pub trait TemporaryHandler: Handler {}

pub struct Temporary<H: TemporaryHandler> {
    inner: H
}

impl<H: TemporaryHandler> Temporary<H> {
    pub fn new(handler: H) -> Self {
        Self { inner: handler }
    }
}

impl<H: TemporaryHandler> Deref for Temporary<H> {
    type Target = H;
    fn deref(&self) -> &Self::Target {
        &self.inner
    }
}

impl<T: TemporaryHandler> Drop for Temporary<T> {
    fn drop(&mut self) {
        fs::remove_file(self.path()).unwrap();
        for dir in self.path().parent().into_iter().rev() {
            if fs::remove_dir(dir).is_err() {
                break
            }
        }
        println!("Droped");
    }
}