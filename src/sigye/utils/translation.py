import gettext as gettextlib
import os
from collections.abc import Callable

import humanize.i18n

# Global translation function
_translator: Callable = gettextlib.gettext


LANG_MAP = {
    "ko_KR": "ko",
}


def init_translations(lang: str = "ko") -> None:
    """
    Initialize translations globally for the entire application.
    Call this once at application startup.
    """
    global _translator
    t_lang = LANG_MAP.get(lang, "en")
    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "locale")
    translations = gettextlib.translation("messages", localedir=localedir, languages=[t_lang], fallback=True)
    translations.install()
    _translator = translations.gettext


def gettext(message: str) -> str:
    """
    Get translated text. This function will use whatever language
    was set up by init_translations().
    """
    return _translator(message)


# Convenience alias that can be imported
_ = gettext


def set_locale(lang: str) -> None:
    """
    Set the locale for translations.
    """
    if lang not in ["en", "en_US", "en_GB"]:
        _ = humanize.i18n.activate(lang)
        _ = init_translations(lang=lang)
