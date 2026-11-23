from solution import Ticket


def setup_function():
    Ticket.reset_counter()


def test_ids():
    a, b, c = Ticket("a"), Ticket("b"), Ticket("c")
    assert (a.id, b.id, c.id) == (1, 2, 3)
    assert Ticket.total_created() == 3


def test_comments_are_per_instance():
    a, b = Ticket("a"), Ticket("b")
    a.add_comment("hi")
    assert a.comments == ["hi"]
    assert b.comments == [], "comments must be created in __init__, not as a class attribute"


def test_reset():
    Ticket("x")
    Ticket.reset_counter()
    assert Ticket("y").id == 1
