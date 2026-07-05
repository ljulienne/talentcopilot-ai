
import streamlit as st

from talentcopilot.i18n.en import translations as EN
from talentcopilot.i18n.fr import translations as FR
from talentcopilot.i18n.zh import translations as ZH


LANGUAGES = {
    "English": EN,
    "Français": FR,
    "中文": ZH,
}


def current_language():

    return st.session_state.get(
        "language",
        "English"
    )


def tr(key: str):

    lang = current_language()

    dictionary = LANGUAGES.get(lang, EN)

    return dictionary.get(key, key)
