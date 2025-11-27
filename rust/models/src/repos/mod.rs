mod dir_repo;
mod file_repo;

pub use dir_repo::DirRepo;
pub use file_repo::FileRepo;

pub trait RepoKey: Eq + std::hash::Hash + serde::Serialize {}
pub trait RepoValue: serde::Serialize {}

impl<T> RepoKey for T where T: Eq + std::hash::Hash + serde::Serialize {}
impl<T> RepoValue for T where T: serde::Serialize {}
