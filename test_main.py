import pytest
import main


def test_get_api_key_success(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text("DEEPSEEK_API_KEY=sk-test-12345", encoding="utf-8")
    
    assert main.get_api_key(str(config_file)) == "sk-test-12345"


def test_get_api_key_file_not_found():
    assert main.get_api_key("test.txt") == ""


def test_get_api_key_wrong_format(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text("WRONG_FORMAT_LINE", encoding="utf-8")
    
    assert main.get_api_key(str(config_file)) == ""





def test_load_reviews_success(tmp_path):
    csv_file = tmp_path / "reviews.csv"
    csv_file.write_text("Отзыв 1\nОтзыв 2\n\nОтзыв 3\n", encoding="utf-8")
    
    result = main.load_reviews(str(csv_file))
    assert result == ["Отзыв 1", "Отзыв 2", "Отзыв 3"]


def test_load_reviews_file_not_found():
    assert main.load_reviews("missing_reviews.csv") == []



def test_analyze_review_error():
    score, category = main.analyze_review(None, "Тестовый отзыв", 1)
    assert score == 5
    assert category == "Кухня"


def test_draw_dashboard_empty_data():
    assert main.draw_dashboard([]) is None