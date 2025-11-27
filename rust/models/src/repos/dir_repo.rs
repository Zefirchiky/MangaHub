use std::marker::PhantomData;

use derive_more::{Deref, DerefMut, IntoIterator};
use handlers::file::{Dir, ModelFileTrait};
use indexmap::IndexMap;
use serde::de::DeserializeOwned;

use crate::repos::{RepoKey, RepoValue};

#[derive(Debug, IntoIterator, Deref, DerefMut)]
pub struct DirRepo<K: RepoKey, V: RepoValue, F: ModelFileTrait> {
    pub dir: Dir,
    #[deref]
    #[deref_mut]
    #[into_iterator(owned, ref, ref_mut)]
    elements: IndexMap<K, V>,
    key_fn: fn(&V) -> K,
    file_name_fn: fn(&K, &V) -> String,
    _file_type: PhantomData<F>,
}

impl<K: RepoKey + DeserializeOwned, V: RepoValue + DeserializeOwned, F: ModelFileTrait>
    DirRepo<K, V, F>
{
    /// Creates a new `DirRepo` instance with the given directory.
    ///
    /// The directory should be unique to this repository, so no other files should be in it.
    ///
    /// # Returns
    ///
    /// A new instance of `DirRepo` with the given directory and an empty index map.
    pub fn new(dir: Dir, key_fn: fn(&V) -> K, file_name_fn: fn(&K, &V) -> String) -> Self {
        Self {
            dir,
            elements: IndexMap::new(),
            key_fn,
            file_name_fn,
            _file_type: PhantomData,
        }
    }

    /// Loads all files in the given directory and deserializes them into the corresponding repository value type.
    ///
    /// # Errors
    ///
    /// Returns Error corresponding to the 'File' type if any of the files in the directory cannot be loaded or deserialized.
    pub fn load(&mut self) -> Result<(), <F as ModelFileTrait>::Error> {
        if let Ok(dir) = self.dir.read_dir() {
            for file_res in dir {
                let file = file_res?;

                let file = F::make_new(file.path());
                let model = file.load_model::<V>()?;
                let key = (self.key_fn)(&model);
                self.insert(key, model);
            }
        }
        Ok(())
    }

    /// Saves all the elements in the repository to their respective files.
    ///
    /// # Errors
    ///
    /// Returns an error if any of the files cannot be saved.
    pub fn save(&self) -> Result<(), <F as ModelFileTrait>::Error> {
        for (key, value) in &self.elements {
            F::make_new(
                self.dir
                    .join(format!("{}.{}", (self.file_name_fn)(key, value), F::ext())),
            )
            .save_model(value)?;
        }
        Ok(())
    }
}
