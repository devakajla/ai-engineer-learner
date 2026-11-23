from solution import eval_rpn


def test_examples():
    assert eval_rpn(["2", "1", "+", "3", "*"]) == 9
    assert eval_rpn(["4", "13", "5", "/", "+"]) == 6


def test_big():
    tokens = ["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]
    assert eval_rpn(tokens) == 22


def test_edges():
    assert eval_rpn(["7"]) == 7
    assert eval_rpn(["-7", "2", "/"]) == -3, "truncate toward zero"
    assert eval_rpn(["7", "-2", "/"]) == -3
    assert eval_rpn(["5", "3", "-"]) == 2, "order of operands"
