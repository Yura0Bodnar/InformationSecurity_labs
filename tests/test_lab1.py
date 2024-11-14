import pytest
from fastapi.testclient import TestClient
from routers.lab1 import router  # Імпортуємо FastAPI роутер
import os
from main import app  # Імпортуємо основний FastAPI додаток

client = TestClient(app)


@pytest.fixture(scope="module")
def valid_input():
    # Додавання коректного вводу для лабораторної роботи
    return 100


@pytest.fixture(scope="module")
def invalid_input_large():
    # Додавання занадто великого вводу для тесту
    return 2000000


@pytest.fixture(scope="module")
def invalid_input_small():
    # Додавання занадто маленького вводу для тесту
    return 5


@pytest.fixture(scope="module")
def invalid_input_non_integer():
    # Додавання нецілого числа
    return "not_a_number"


def test_lab1_valid_input(valid_input):
    # Тестуємо успішний запит
    response = client.post("/lab1", data={"inputLab1": valid_input})
    assert response.status_code == 200
    data = response.json()

    # Перевіряємо наявність результатів
    assert "pi_lcg_result" in data
    assert "pi_random_result" in data
    assert "known_pi" in data
    assert "sequence_result" in data
    assert "period" in data


def test_lab1_invalid_input_large(invalid_input_large):
    # Тестуємо випадок з занадто великим числом
    response = client.post("/lab1", data={"inputLab1": invalid_input_large})
    assert response.status_code == 200
    assert "Надто велике число, введіть менше n." in response.text


def test_lab1_invalid_input_small(invalid_input_small):
    # Тестуємо випадок з занадто малим числом
    response = client.post("/lab1", data={"inputLab1": invalid_input_small})
    assert response.status_code == 200
    assert "Замале n. Введіть більше число." in response.text


def test_lab1_file_results():
    response = client.post("/lab1", data={"inputLab1": 100})  # Викликаємо пост-запит
    assert response.status_code == 200  # Перевіряємо, що статус відповіді 200
    data = response.json()  # Отримуємо JSON-відповідь

    # Перевіряємо, чи є в відповіді правильні ключі
    assert "pi_lcg_result" in data
    assert "pi_random_result" in data
    assert "known_pi" in data
    assert "sequence_result" in data
    assert "period" in data
    assert "chesaro" in data
    assert "random_sequence" in data


def test_download_results():
    # Створюємо тестовий файл
    with open("results.txt", "w") as f:
        f.write("Test data for results file.")

    # Викликаємо ендпоінт для завантаження файлу
    response = client.get("/download_results")

    # Перевіряємо, що файл є в відповіді
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == 'attachment; filename="results.txt"'

    # Перевіряємо, чи файл містить правильні дані
    content = response.content.decode("utf-8")
    assert "Test data for results file." in content

    # Видаляємо файл після тестування
    os.remove("results.txt")

