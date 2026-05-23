"""Tema sabitlerinin var ve doğru tipte olduğunu doğrular (smoke)."""

import re

from ui import theme


HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def test_renk_sabitleri_hex_formatinda():
    for ad in [
        "ARKA_PLAN_ANA",
        "ARKA_PLAN_KART",
        "ARKA_PLAN_OVERLAY",
        "KENAR_INCE",
        "KENAR_KALIN",
        "METIN_ANA",
        "METIN_IKINCIL",
        "METIN_PASIF",
        "AKSAN",
        "AKSAN_KOYU",
        "VURGU",
        "BEKLEME",
        "MAVI_VURGU",
    ]:
        deger = getattr(theme, ad)
        assert isinstance(deger, str), f"{ad} string olmalı"
        assert HEX_RE.match(deger), f"{ad} '{deger}' hex formatında değil"


def test_font_sabitleri_tup_uc_eleman():
    assert theme.FONT_GOVDE[0] == "Georgia"
    assert isinstance(theme.FONT_GOVDE[1], int)
    assert theme.FONT_BASLIK[0] == "Georgia"


def test_stylesheet_uretir():
    css = theme.qt_stylesheet()
    assert isinstance(css, str)
    assert theme.AKSAN in css
    assert theme.ARKA_PLAN_ANA in css
