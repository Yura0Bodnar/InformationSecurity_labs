import pytest
from io import BytesIO
import os
from fastapi.testclient import TestClient
from main import app  # Імпортуємо основний FastAPI додаток
import hashlib

client = TestClient(app)

@pytest.fixture
def create_test_file():
    """Фікстура для створення тестового файлу"""
    def _create_file(content, filename="test_file.txt"):
        with open(filename, "wb") as f:
            f.write(content)
        return filename
    yield _create_file
    # Видаляємо файл після завершення тесту
    if os.path.exists("test_file.txt"):
        os.remove("test_file.txt")


def test_md5_string():
    """Тест для хешування рядка"""
    input_string = "Hello, World!"
    expected_md5 = hashlib.md5(input_string.encode()).hexdigest()

    response = client.post("/lab2/md5_string", data={"input_string": input_string})

    assert response.status_code == 200
    data = response.json()
    assert "string_result" in data
    assert data["string_result"] == expected_md5


def test_download_results_lab2(create_test_file):
    """Тест для завантаження результатів хешування"""
    # Створюємо тестовий файл результатів
    create_test_file(b"Hash code:\nfc3ff98e8c6a0d3087d515c0473f8677\n\n", "result_md5.txt")

    response = client.get("/download_results_lab2")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    content = response.json()
    assert content["status"] == "success"
    assert "fc3ff98e8c6a0d3087d515c0473f8677" in content["content"]

    os.remove("result_md5.txt")  # Очищення після тесту


def test_verify_file(create_test_file):
    """Тест для перевірки цілісності файлу"""
    # Створюємо файл з вмістом і його хешем
    file_content = b"File content to verify."
    filename = create_test_file(file_content)
    file_hash = hashlib.md5(file_content).hexdigest()

    # Створюємо файл із хешем
    hash_filename = "file_hash.txt"
    with open(hash_filename, "w") as f:
        f.write(file_hash)

    # Викликаємо ендпоінт перевірки
    with open(hash_filename, "rb") as hash_file:
        response = client.post("/lab2/verify_file", data={"file_hash": file_hash}, files={"hash_file": hash_file})

    assert response.status_code == 200
    data = response.json()
    assert "is_intact" in data
    assert data["is_intact"] is True

    # Очищення після тесту
    os.remove(hash_filename)
