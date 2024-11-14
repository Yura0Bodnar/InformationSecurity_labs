import pytest
from fastapi.testclient import TestClient
from main import app  # Замініть `main` на ім'я вашого файлу з FastAPI додатком
import os

client = TestClient(app)


@pytest.fixture(scope="module")
def generate_keys():
    """
    Генерація ключів перед запуском тестів.
    """
    response = client.post("/lab5/generate_keys")
    assert response.status_code == 200
    assert "DSA ключі згенеровані та збережені у файли." in response.text


def test_generate_keys(generate_keys):
    """
    Перевірка генерації ключів.
    """
    assert os.path.exists("dsa_private_key.pem"), "Приватний ключ не створено"
    assert os.path.exists("dsa_public_key.pem"), "Публічний ключ не створено"


def test_sign_data(generate_keys):
    """
    Тест підпису тексту.
    """
    # Відправляємо текст на підпис
    response = client.post("/lab5/sign_data", data={"input_text_dsa": "Hello, DSA!"})
    assert response.status_code == 200

    # Перевіряємо, чи текст для підпису є у HTML
    assert "Hello, DSA!" in response.text, "Текст для підпису не відображається в HTML-відповіді"

    # Перевіряємо, чи результат підпису відображається у HTML
    assert "<h4>DSA підпис:</h4>" in response.text, "Заголовок результату підпису не відображається"
    assert "Завантажити результат" in response.text, "Кнопка для завантаження підпису не відображається"

    # Перевіряємо наявність самого підпису
    start_index = response.text.find("<p>") + len("<p>")
    end_index = response.text.find("</p>")
    signature = response.text[start_index:end_index]
    assert signature, "Результат підпису (DSA) не відображається"


def test_sign_file(generate_keys, tmp_path):
    """
    Тест підпису файлу.
    """
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("This is a test file for DSA!")

    with open(test_file, "rb") as f:
        response = client.post("/lab5/sign_file", files={"file": f})

    assert response.status_code == 200
    assert "Файл успішно підписано" in response.text
