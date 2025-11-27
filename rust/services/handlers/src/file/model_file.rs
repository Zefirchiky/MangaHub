use serde::{Serialize, de::DeserializeOwned};

use crate::file::FileTrait;

pub trait ModelIoError: From<std::io::Error> {}

pub trait ModelFileTrait: FileTrait {
    type Error: ModelIoError;

    fn save_model(&self, model: &impl Serialize) -> Result<(), Self::Error>;
    fn load_model<T: DeserializeOwned>(&self) -> Result<T, Self::Error>;
}
