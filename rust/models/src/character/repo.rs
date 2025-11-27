use derive_more::{Deref, DerefMut, From};
use handlers::file::Json;
use indexmap::IndexMap;

use crate::{character::Character, repos::FileRepo};

#[derive(Debug, From, Deref, DerefMut)]
pub struct Repo {
    #[deref]
    #[deref_mut]
    pub characters: FileRepo<uuid::Uuid, Character, Json>,
    character_names_map: IndexMap<String, uuid::Uuid>,
    character_surnames_map: IndexMap<String, uuid::Uuid>,
}

impl Repo {
    pub fn new(file: Json) -> Self {
        Self {
            characters: FileRepo::new(file),
            character_names_map: IndexMap::new(),
            character_surnames_map: IndexMap::new(),
        }
    }

    pub fn get_from_name(&self, name: &str) -> Option<&Character> {
        let id = self.character_names_map.get(name)?;
        self.characters.get(id)
    }

    pub fn get_from_surname(&self, surname: &str) -> Option<&Character> {
        let id = self.character_surnames_map.get(surname)?;
        self.characters.get(id)
    }

    pub fn add_character(&mut self, character: Character) {
        self.add_character_name_id(character.name.clone(), character.id);
        self.add_character_surname_id(character.name.clone(), character.id);
        self.characters.insert(character.id, character);
    }

    pub fn add_character_name_id(&mut self, name: String, id: uuid::Uuid) {
        if !name.is_empty() {
            self.character_names_map.insert(name, id);
        }
    }

    pub fn add_character_surname_id(&mut self, surname: String, id: uuid::Uuid) {
        if !surname.is_empty() {
            self.character_names_map.insert(surname, id);
        }
    }
}
