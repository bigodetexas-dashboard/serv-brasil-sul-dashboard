from flask import request, session
from flask_babel import Babel


def get_locale():
    # 1. Manually specified via URL parameter
    lang = request.args.get("lang")
    if lang:
        session["lang"] = lang
        return lang

    # 2. Saved in session
    if "lang" in session:
        return session["lang"]

    # 3. Automatically detected from browser
    return request.accept_languages.best_match(
        ["pt", "en", "es", "fr", "it", "de", "ru", "zh_Hans", "ja", "ko"]
    )


def init_babel(app):
    babel = Babel(app, locale_selector=get_locale)
    return babel
