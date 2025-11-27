use std::{fs::File, io::Write, path::Path};

use derive_more::{AsRef, Deref, DerefMut, From};
use serde::{Deserialize, Serialize, de::DeserializeOwned};

use crate::file::{FileBase, FileTrait, ModelFileTrait, model_file::ModelIoError};

#[derive(Debug, thiserror::Error)]
pub enum ModelJsonIoError {
    #[error("Seder Error: {0}")]
    Serde(#[from] serde_json::Error),
    #[error("Io Error: {0}")]
    Io(#[from] std::io::Error),
}

impl ModelIoError for ModelJsonIoError {}

#[derive(Debug, Clone, Default, From, AsRef, Deref, DerefMut, Serialize, Deserialize)]
#[from(forward)]
#[as_ref(forward)]
pub struct Json {
    handler: FileBase,
}

impl Json {
    /// Creates a new JsonHandler for the given file.
    ///
    /// If the file does not exist, it will be created. If the parent directories do not exist, they will be created.
    ///
    /// # Panics
    ///
    /// Panics if the path exists but is not a file, or if the file does not have the correct extension.
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self::make_new(file)
    }
}

impl FileTrait for Json {
    fn make_new(file: impl AsRef<Path>) -> Self {
        Self {
            handler: FileBase::new_with_handler::<Self>(file),
        }
    }

    fn initialize_file(file: &mut File) {
        file.write_all(b"{}")
            .expect("Failed to write initial JSON content");
    }

    fn ext() -> &'static str {
        "json"
    }
}

impl ModelFileTrait for Json {
    type Error = ModelJsonIoError;

    fn load_model<T: DeserializeOwned>(&self) -> Result<T, Self::Error> {
        let data = self.load()?;
        Ok(serde_json::from_str(&data)?)
    }

    fn save_model(&self, model: &impl Serialize) -> Result<(), Self::Error> {
        self.save(serde_json::to_string_pretty(model)?)?;
        Ok(())
    }
}

impl From<&str> for Json {
    fn from(value: &str) -> Self {
        Self::new(value)
    }
}

#[cfg(test)]
mod json_tests {
    use std::fs;

    use crate::file::{Json, Temporary};

    static FILE_NAME_EXT: &str = "dis/init.json";
    static TEMP_FILE_NAME_EXT: &str = "dis/init_temp.json";
    static FILE_NAME: &str = "dis/init";
    static TEMP_FILE_NAME: &str = "dis/init_temp";

    #[test]
    fn init() {
        Json::new(FILE_NAME_EXT);
        assert!(
            fs::exists(FILE_NAME_EXT).unwrap_or(false),
            "File {FILE_NAME_EXT} was not created"
        );
    }

    #[test]
    #[should_panic]
    fn init_wrong_ext() {
        Json::new(FILE_NAME);
    }

    #[test]
    fn init_temp() {
        {
            let _tis = Temporary::new(Json::new(TEMP_FILE_NAME_EXT));
            assert!(
                fs::exists(TEMP_FILE_NAME_EXT).unwrap_or(false),
                "File {TEMP_FILE_NAME_EXT} was not created"
            );
        }
        assert!(
            !fs::exists(TEMP_FILE_NAME_EXT).unwrap_or(false),
            "File {TEMP_FILE_NAME_EXT} was not deleted"
        );
    }

    #[test]
    #[should_panic]
    fn init_temp_wrong_ext() {
        Temporary::new(Json::new(TEMP_FILE_NAME));
    }
}
