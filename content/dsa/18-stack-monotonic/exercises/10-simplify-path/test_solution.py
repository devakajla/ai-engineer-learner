from solution import simplify_path


def test_examples():
    assert simplify_path("/home//foo/") == "/home/foo"
    assert simplify_path("/a/./b/../../c/") == "/c"


def test_edges():
    assert simplify_path("/") == "/"
    assert simplify_path("/../") == "/", "cannot go above the root"
    assert simplify_path("/...") == "/...", "three dots is a normal name"
    assert simplify_path("/a/b/c/../..") == "/a"
    assert simplify_path("///a///b///") == "/a/b"
