use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[allow(dead_code)]
#[derive(Serialize, Deserialize)]
pub enum CharacterSex {
    Male,
    Female,
    Asexual,
    Hermafrodite,
    Unknown,
}

impl Default for CharacterSex {
    fn default() -> Self {
        CharacterSex::Unknown
    }
}

#[allow(dead_code)]
#[derive(Default, Serialize, Deserialize)]
pub struct Character {
    pub id: Uuid,
    pub name: String,
    pub surname: String,
    pub age: usize,
    pub sex: CharacterSex,
}

impl Character {
    pub fn new() -> Self {
        Character {
            id: Uuid::new_v4(),
            ..Default::default()
        }
    }
}