use crate::character::Repo;

pub struct Context {
    pub novel: NovelContext,
    pub chapter: ChapterContext,
    pub paragraph: ParagraphContext,
}

pub struct NovelContext {
    pub spell_checker: spel_right::SpellChecker,
    pub character_repo: Repo,
}

pub struct ChapterContext {

}

pub struct ParagraphContext {

}