import pytest

from similarity import Similarity

similarity_=Similarity()
def test_numeric_similarity_exact_match():
    assert similarity_.numeric_similarity(5, 5) == pytest.approx(1.0, abs=0.1)
    assert similarity_.numeric_similarity(15, 15) == pytest.approx(1.0, abs=0.1)
    assert similarity_.numeric_similarity(0.5, 0.5) == pytest.approx(1.0, abs=0.1)

def test_numeric_similarity_close_match():
    assert similarity_.numeric_similarity(5, 6) == pytest.approx(0.95, abs=0.1)
    assert similarity_.numeric_similarity(15, 14) == pytest.approx(0.95, abs=0.1)
    assert similarity_.numeric_similarity(0.5, 0.6) == pytest.approx(0.95, abs=0.1)

def test_numeric_similarity_large_difference():
    assert similarity_.numeric_similarity(5, 50) == pytest.approx(0.2, abs=0.2)
    assert similarity_.numeric_similarity(150, 15) == pytest.approx(0.2, abs=0.2)
    assert similarity_.numeric_similarity(0.5, 5.0) == pytest.approx(0.8, abs=0.2)

def test_string_similarity_exact_match():
    assert similarity_.string_similarity("hello", "hello") == pytest.approx(1.0, abs=0.1)
    assert similarity_.string_similarity("apple", "apple") == pytest.approx(1.0, abs=0.1)
    assert similarity_.string_similarity("12345", "12345") == pytest.approx(1.0, abs=0.1)

def test_string_similarity_close_match():
    assert similarity_.string_similarity("hello", "hella") == pytest.approx(0.94, abs=0.2)
    assert similarity_.string_similarity("apple", "appli") == pytest.approx(0.94, abs=0.2)
    assert similarity_.string_similarity("12345", "12346") == pytest.approx(0.94, abs=0.2)

def test_string_similarity_large_difference():
    assert similarity_.string_similarity("hello", "world") == pytest.approx(0.3, abs=0.2)
    assert similarity_.string_similarity("apple", "banana") == pytest.approx(0.3, abs=0.2)
    assert similarity_.string_similarity("12345", "67890") == pytest.approx(0.2, abs=0.2)

def test_compare_parameters_exact_match():
    dict1 = {"name": "John", "age": 30, "city": "New York"}
    dict2 = {"name": "John", "age": 30, "city": "New York"}
    assert similarity_.get_similarity(dict1, dict2) == pytest.approx(1.0, abs=0.01)

def test_compare_parameters_partial_match():
    dict3 = {"name": "Alice", "age": 25, "city": "Los Angeles"}
    dict4 = {"name": "Alice", "age": 26, "city": "San Francisco"}
    assert similarity_.get_similarity(dict3, dict4) == pytest.approx(0.8, abs=0.2)

def test_compare_parameters_no_match():
    dict5 = {"name": "Bob", "age": 35, "city": "Chicago"}
    dict6 = {"name": "Tom", "ages": 30, "cityes": "Houston"}
    assert similarity_.get_similarity(dict5, dict6) == pytest.approx(0.5, abs=0.2)

if __name__ == "__main__":
    pytest.main()
