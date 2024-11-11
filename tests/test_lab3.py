import pytest
from fastapi.testclient import TestClient
from routers.lab3 import router
import hashlib

# Ініціалізуємо клієнт для тестування
client = TestClient(router)


# Тест для встановлення пароля
def test_set_password():
    response = client.post("/lab3/set_password", data={"password": "secretpassword"})
    assert response.status_code == 200
    assert response.json() == {"message": "Password saved successfully."}


# Тест для шифрування тексту
def test_encrypt_text():
    # Спочатку встановимо пароль
    client.post("/lab3/set_password", data={"password": "secretpassword"})

    # Тестуємо шифрування
    response = client.post("/lab3/encrypt_text", data={"input_text": "Hello World"})

    assert response.status_code == 200
    assert "Encrypted text" in response.json()["message"]


# Тест для дешифрування тексту
def test_decrypt_text():
    # Спочатку встановимо пароль
    client.post("/lab3/set_password", data={"password": "secretpassword"})

    # Спочатку зашифруємо текст
    encrypt_response = client.post("/lab3/encrypt_text", data={"input_text": "Hello World"})
    encrypted_text = encrypt_response.json()["message"].replace("Encrypted text: ", "")

    # Тепер дешифруємо текст
    response = client.post("/lab3/decrypt_text", data={"input_text": encrypted_text, "password": "secretpassword"})

    assert response.status_code == 200
    assert "Decrypted text" in response.json()["message"]
    assert response.json()["message"] == "Decrypted text: Hello World"


# Тест для шифрування файлу
def test_encrypt_file():
    # Створюємо тестовий файл
    file_content = b"Test file content"
    file_name = "testfile.txt"

    with open(file_name, "wb") as f:
        f.write(file_content)

    # Спочатку встановимо пароль
    client.post("/lab3/set_password", data={"password": "secretpassword"})

    # Тестуємо шифрування файлу
    with open(file_name, "rb") as f:
        response = client.post("/lab3/encrypt_file", files={"encrypt_file": (file_name, f, "text/plain")})

    assert response.status_code == 200
    assert "File encrypted" in response.json()["message"]


# Тест для обробки файлу з непідтримуваним форматом
def test_invalid_password_decryption():
    # Create and encrypt a test file
    file_content = b"Test file content for decryption"
    file_name = "testfile.txt"

    with open(file_name, "wb") as f:
        f.write(file_content)

    # Set the password first
    client.post("/lab3/set_password", data={"password": "secretpassword"})

    # Encrypt the file
    with open(file_name, "rb") as f:
        encrypt_response = client.post("/lab3/encrypt_file", files={"encrypt_file": (file_name, f, "text/plain")})

    # Now attempt to decrypt with an incorrect password
    with open(file_name, "rb") as f:
        response = client.post("/lab3/decrypt_file", files={"decrypt_file": (file_name, f, "text/plain")},
                               data={"password": "wrongpassword"})

    assert response.status_code == 400
    assert "Incorrect password!" in response.json()["message"]
