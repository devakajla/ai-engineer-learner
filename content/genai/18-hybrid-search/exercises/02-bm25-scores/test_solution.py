import math

import pytest

from solution import bm25_scores


def test_examples():
    scores = bm25_scores("b", ["a b", "a c c"])
    assert scores[0] == pytest.approx(0.7617, abs=1e-3)
    assert scores[1] == 0.0
    assert bm25_scores("zzz", ["a b", "a c c"]) == [0.0, 0.0]
    assert bm25_scores("a", []) == []


def test_hand_calculated_value():
    # N = 2, df = 1, idf = ln(2). doc 0: tf = 1, length 2, avg length 2.5
    idf = math.log(2)
    norm = 1 + 1.5 * (1 - 0.75 + 0.75 * 2 / 2.5)
    assert bm25_scores("b", ["a b", "a c c"])[0] == pytest.approx(idf * 1 * 2.5 / norm)


def test_rare_word_beats_common_word():
    docs = ["error code 429", "error in the app", "error while saving", "an error"]
    scores = bm25_scores("error 429", docs)
    assert scores.index(max(scores)) == 0
    assert scores[0] > scores[1]


def test_more_occurrences_and_shorter_docs_score_higher():
    same_length = bm25_scores("task", ["task task x", "task y z"])
    assert same_length[0] > same_length[1]
    short_vs_long = bm25_scores("task", ["task a", "task a b c d e f g h"])
    assert short_vs_long[0] > short_vs_long[1], "a short document with the word beats a long one"


def test_query_words_are_counted_once_and_case_is_ignored():
    docs = ["Delete a task", "list tasks"]
    assert bm25_scores("delete delete", docs) == pytest.approx(bm25_scores("DELETE", docs))


def test_empty_documents():
    assert bm25_scores("a", ["", ""]) == [0.0, 0.0]
    assert bm25_scores("", ["a b"]) == [0.0]
    assert all(type(s) is float for s in bm25_scores("a", ["a", "b"]))
