from solution import first_unique_char


def test_examples():
    assert first_unique_char("leetcode") == 0
    assert first_unique_char("aabbcd") == 4
    assert first_unique_char("aabb") == -1


def test_more():
    assert first_unique_char("") == -1
    assert first_unique_char("z") == 0
    assert first_unique_char("loveleetcode") == 2
