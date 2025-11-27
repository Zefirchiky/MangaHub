use derive_more::{Deref, DerefMut};
use handlers::file::{Dir, Json, ModelJsonIoError};
use indexmap::IndexMap;
use uuid::Uuid;

use crate::{repos::DirRepo, site::Site};

#[derive(Debug, Deref, DerefMut)]
pub struct Repo {
    #[deref]
    #[deref_mut]
    repo: DirRepo<Uuid, Site, Json>,
    name_to_id: IndexMap<String, Uuid>,
}

impl Repo {
    pub fn new(dir: Dir) -> Self {
        Self {
            repo: DirRepo::new(
                dir,
                |site| site.id,
                |&key, site| format!("{}_{}", site.name, key),
            ),
            name_to_id: IndexMap::new(),
        }
    }

    pub fn get_by_name(&self, name: &str) -> Option<&Site> {
        self.get(self.name_to_id.get(&name.to_lowercase())?)
    }

    pub fn load(&mut self) -> Result<(), ModelJsonIoError> {
        self.repo.load()
    }

    pub fn save(&self) -> Result<(), ModelJsonIoError> {
        self.repo.save()
    }
}
