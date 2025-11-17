use std::{fs, path::{Path, PathBuf}};

use derive_more::{Deref, DerefMut};
use handlers::file::{Json, ModelFileTrait};
use indexmap::IndexMap;
use log::warn;
use uuid::Uuid;

use crate::{repos::RepoBase, site::Site};

#[derive(Debug, Deref, DerefMut)]
pub struct Repo {
    #[deref]
    #[deref_mut]
    repo: RepoBase<Uuid, Site>,
    name_to_id: IndexMap<String, Uuid>,
}

impl Repo {
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self {
            repo: RepoBase::new(file),
            name_to_id: IndexMap::new(),
        }
    }

    pub fn get_by_name(&self, name: &str) -> Option<&Site> {
        self.get(self.name_to_id.get(&name.to_lowercase())?)
    }

    pub fn load(&mut self) {
        let dir = match fs::read_dir(self.file.file.parent().unwrap()) {
            Ok(dir) => dir,
            Err(err) => {
                warn!("Failed to read directory: {}", err);
                return;
            }
        };

        for file_res in dir {
            let file = match file_res {
                Ok(file) => file,
                Err(err) => {
                    warn!("Failed to read file: {}", err);
                    continue;
                }
            };

            let name = file.file_name().into_string().unwrap();
            if !name.ends_with(".json") || !name.contains('_') {
                continue;
            }

            let (slug, id) = match name.split_once('_') {
                Some((slug, id)) => (slug.to_string(), id.to_string()),
                None => continue,
            };

            let file_path = self.file.file.parent().unwrap().join(format!("test_full/{slug}_{id}.json"));
            let handler = Json::new(&file_path);
            let site = match handler.load_model::<Site>() {
                Ok(site) => site,
                Err(err) => {
                    warn!("Failed to load site from {}: {}", file_path.display(), err);
                    continue;
                }
            };

            self.name_to_id.insert(site.name.to_lowercase(), site.id.clone());
            self.insert(site.id.clone(), site);
        }
    }

    pub fn save(&self) {
        for (id, site) in self.iter() {
            let file_name = format!("{}_{id}.json", site.name);
            let file_path = self.file.file.parent().unwrap().join(file_name);
            let file_handler = Json::new(file_path);
            if let Err(err) = file_handler.save_model(site) {
                warn!("Failed to save site {} ({id}): {err}", site.name)
            }
        }
    }
}
