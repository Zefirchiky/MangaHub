from config import Config

def get_id_from_name(name: str) -> str:
    id_ = name.lower()
    for s1, s2 in Config.DataProcessing.UrlParsing.replace_symbols().items():
        id_ = id_.replace(s1, s2)
    return id_