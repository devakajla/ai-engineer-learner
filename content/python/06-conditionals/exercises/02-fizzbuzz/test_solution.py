from solution import fizzbuzz


def test_examples():
    assert fizzbuzz(15) == "FizzBuzz"
    assert fizzbuzz(9) == "Fizz"
    assert fizzbuzz(7) == "7"


def test_more():
    assert fizzbuzz(10) == "Buzz"
    assert fizzbuzz(30) == "FizzBuzz", "30 is divisible by 3 and 5"
    assert fizzbuzz(1) == "1"
    assert fizzbuzz(0) == "FizzBuzz", "0 is divisible by everything"
    assert isinstance(fizzbuzz(4), str), "return a string, not an int"
