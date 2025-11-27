use derive_more::{Deref, DerefMut, From};
use handlers::file::{Json, ModelJsonIoError};
use indexmap::IndexMap;
use uuid::Uuid;

use crate::{media::MediaTrait, repos};

#[derive(Debug, From, Deref, DerefMut)]
#[from(forward)]
pub struct RepoBase<M: MediaTrait> {
    #[deref]
    #[deref_mut]
    repo: repos::FileRepo<uuid::Uuid, M, Json>,
    slug_to_id: IndexMap<String, Uuid>,
}

impl<M: MediaTrait> RepoBase<M> {
    pub fn new(file: Json) -> Self {
        Self {
            repo: repos::FileRepo::new(file),
            slug_to_id: IndexMap::new(),
        }
    }

    pub fn get_by_slug(&self, name_slug: &str) -> Option<&M> {
        self.get(self.slug_to_id.get(name_slug)?)
    }

    pub fn get_by_name(&self, name: &str) -> Option<&M> {
        self.get_by_slug(&slug::slugify(name.to_lowercase()))
    }

    pub fn insert(&mut self, media: M) -> Option<M> {
        let meta = media.metadata();
        self.slug_to_id.insert(meta.slug.clone(), meta.id);
        self.repo.insert(meta.id, media)
    }

    pub fn load(&mut self) -> Result<(), ModelJsonIoError> {
        self.repo.load()?;
        for (id, media) in self.repo.iter() {
            self.slug_to_id
                .insert(media.metadata().slug.clone(), id.clone());
        }
        Ok(())
    }
}
