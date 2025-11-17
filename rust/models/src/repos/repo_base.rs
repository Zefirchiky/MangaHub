use std::{hash::Hash, path::Path};

use derive_more::{Deref, DerefMut, IntoIterator};
use handlers::file::{Json, ModelFileTrait, ModelJsonIoError};
use indexmap::IndexMap;
use serde::{Deserialize, Serialize, de::DeserializeOwned};

pub trait RepoKey: Eq + Hash + Serialize {}
pub trait RepoValue: Serialize {}

impl<T> RepoKey for T where T: Eq + Hash + Serialize {}
impl<T> RepoValue for T where T: Serialize {}

#[derive(Debug, IntoIterator, Deref, DerefMut, Serialize, Deserialize)]
pub struct RepoBase<K: RepoKey, V: RepoValue> {
    #[serde(skip)]
    pub file: Json,
    #[deref]
    #[deref_mut]
    #[into_iterator(owned, ref, ref_mut)]
    elements: IndexMap<K, V>,
}

impl<K: RepoKey + DeserializeOwned, V: RepoValue + DeserializeOwned> RepoBase<K, V> {
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self {
            file: Json::new(file),
            elements: IndexMap::new(),
        }
    }

    pub fn load(f: &Json) -> Result<Self, ModelJsonIoError> {
        f.load_model::<Self>()
    }

    pub fn save(&self) -> Result<(), ModelJsonIoError> {
        self.file.save_model(self)
    }
}