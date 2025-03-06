from enum import Enum


class IconsEnum(Enum):
    """Enum for all default icons names. Used to get icons from IconRepo."""
    
    # UTILS
    EYE = 'eye'
    NOT_EYE = 'not_eye'
    Q_MARK = 'question_mark'
    ADD = 'add'
    SAVE = 'save'
    
    # NAVIGATION
    L_ARROW = 'left'
    R_ARROW = 'right'
    L_ARROW_FULL = 'left_full'
    R_ARROW_FULL = 'right_full'
    CLOSE = 'close'
    MENU = 'menu'
    SETTINGS = 'settings'
    MAP = 'map'
    
    # MEDIA
    MANGA = 'manga'
    NOVEL = 'novel'
    
    # TEST
    TEST = 'airplane-outline'