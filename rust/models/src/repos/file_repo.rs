use derive_more::{Deref, DerefMut, IntoIterator};
use handlers::file::ModelFileTrait;
use indexmap::IndexMap;
use serde::de::DeserializeOwned;

use crate::repos::{RepoKey, RepoValue};

/// A repository that stores serializable models.
///
/// Is able to save and load them into and from a `File`.
#[derive(Debug, IntoIterator, Deref, DerefMut)]
pub struct FileRepo<K: RepoKey, V: RepoValue, F: ModelFileTrait> {
    pub file: F,
    #[deref]
    #[deref_mut]
    #[into_iterator(owned, ref, ref_mut)]
    elements: IndexMap<K, V>,
}

impl<K: RepoKey + DeserializeOwned, V: RepoValue + DeserializeOwned, F: ModelFileTrait>
    FileRepo<K, V, F>
{
    pub fn new(file: F) -> Self {
        Self {
            file,
            elements: IndexMap::new(),
        }
    }

    pub fn load(&mut self) -> Result<(), F::Error> {
        self.elements = self.file.load_model::<IndexMap<K, V>>()?;
        Ok(())
    }

    pub fn save(&self) -> Result<(), F::Error> {
        self.file.save_model(&self.elements)
    }
}
