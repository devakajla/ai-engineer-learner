from types import SimpleNamespace as NS


def chunk(text):
    return NS(choices=[NS(delta=NS(content=text))])

from solution import chunk_text


def test_text():
    assert chunk_text(chunk("Hel")) == "Hel"


def test_none_content():
    assert chunk_text(chunk(None)) == ""


def test_no_choices():
    assert chunk_text(NS(choices=[])) == ""


def test_empty_text_stays():
    assert chunk_text(chunk("")) == ""
