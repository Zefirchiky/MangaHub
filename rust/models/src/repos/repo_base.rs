use std::{hash::Hash, ops::{Deref, DerefMut}, path::Path};

use handlers::JsonHandler;
use indexmap::{IndexMap};
use serde::{de::DeserializeOwned, Deserialize, Serialize};

pub trait RepoKey: Eq + Hash + Serialize {}
pub trait RepoValue: Serialize {}

impl<T> RepoKey for T where T: Eq + Hash + Serialize {}
impl<T> RepoValue for T where T: Serialize {}

#[derive(Debug, Serialize, Deserialize)]
pub struct RepoBase<K: RepoKey, V: RepoValue> {
    #[serde(skip)]
    file_handler: JsonHandler,
    elements: IndexMap<K, V>,
}

impl<K: RepoKey + DeserializeOwned, V: RepoValue + DeserializeOwned> RepoBase<K, V> {
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self {
            file_handler: JsonHandler::new(file),
            elements: IndexMap::new(),
        }
    }

    pub fn load(&self) -> Result<Self, serde_json::Error> {
        self.file_handler.load::<Self>()
    }

    pub fn save(&self) -> Result<(), serde_json::Error> {
        self.file_handler.save(self)
    }
}

impl<K: RepoKey, V: RepoValue> Deref for RepoBase<K, V> {
    type Target = IndexMap<K, V>;
    fn deref(&self) -> &Self::Target {
        &self.elements
    }
}

impl<K: RepoKey, V: RepoValue> DerefMut for RepoBase<K, V> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.elements
    }
}

impl<K: RepoKey, V: RepoValue> Drop for RepoBase<K, V> {
    fn drop(&mut self) {
        if let Result::Err(err) = self.file_handler.save(self) {
            eprintln!("{err}");
        }
    }
}