import pytest
from fastapi.testclient import TestClient
from main import app  # замініть на ваш основний файл програми
import os
from routers.lab4 import load_public_key, encrypt_message, load_private_key, encrypt_file

client = TestClient(app)


def test_generate_key():
    # Виклик ендпоінта
    response = client.post("/lab4/generate_key")

    # Перевірка статусу відповіді
    assert response.status_code == 200, "Статус відповіді не є 200 OK"

    # Перевірка вмісту HTML-відповіді
    assert "Ключі успішно згенеровані та збережені у файли." in response.text, "Повідомлення про успішну генерацію ключів не знайдено"

    # Перевірка, чи файли ключів існують
    assert os.path.exists("private_key.pem"), "Файл private_key.pem не створений"
    assert os.path.exists("public_key.pem"), "Файл public_key.pem не створений"


# def test_rsa_hash_string():
#     test_text = "Тестове повідомлення"
#
#     # Генерація ключів
#     if not os.path.exists("private_key.pem") or not os.path.exists("public_key.pem"):
#         from routers.lab4 import generate_keys
#         generate_keys()
#
#     public_key = load_public_key()
#     expected_encrypted_message = encrypt_message(test_text, public_key).hex()
#
#     response = client.post("/lab4/rsa_string", data={"input_text_rsa": test_text})
#
#     # Логи для перевірки
#     print("Expected encrypted message:", expected_encrypted_message)
#     print("Response text:", response.text)
#
#     assert response.status_code == 200, "Статус відповіді не є 200 OK"
#     assert expected_encrypted_message in response.text, "Шифрування тексту не відображено у шаблоні"

def test_download_results():
    # Створюємо тестовий файл
    test_filename = "result_rsa.txt"
    with open(test_filename, "w") as f:
        f.write("Це тестовий файл результатів.")

    # Викликаємо ендпоінт
    response = client.get("/lab4/download_results")

    # Перевіряємо статус відповіді
    assert response.status_code == 200, "Статус відповіді не є 200 OK"
    assert response.headers["content-type"] == "application/octet-stream", "Тип контенту неправильний"
    assert response.headers["content-disposition"].startswith("attachment"), "Файл не позначено як attachment"

    # Видаляємо тестовий файл
    os.remove(test_filename)


def test_download_results_file_not_found():
    # Переконаємося, що файл не існує
    test_filename = "result_rsa.txt"
    if os.path.exists(test_filename):
        os.remove(test_filename)

    # Викликаємо ендпоінт
    response = client.get("/lab4/download_results")

    # Перевіряємо статус відповіді
    assert response.status_code == 404, "Статус відповіді не є 404 Not Found"
    assert response.json()["detail"] == "Файл не знайдено.", "Текст помилки неправильний"


def test_decrypt_string_success():
    # Тестовий текст
    test_text = "Тестове повідомлення"

    # Генеруємо ключі, якщо їх немає
    if not os.path.exists("private_key.pem") or not os.path.exists("public_key.pem"):
        from routers.lab4 import generate_keys
        generate_keys()

    # Завантажуємо ключі
    public_key = load_public_key()
    private_key = load_private_key()

    # Шифруємо текст
    encrypted_data = encrypt_message(test_text, public_key).hex()

    # Викликаємо ендпоінт для дешифрування
    response = client.post("/lab4/decrypt_string", data={"encrypted_text": encrypted_data})

    # Перевіряємо статус відповіді
    assert response.status_code == 200, "Статус відповіді не є 200 OK"
    assert response.json()["status"] == "success", "Статус відповіді не успішний"
    assert response.json()["decrypted_result"] == test_text, "Дешифрований текст не збігається з оригіналом"


def test_decrypt_string_error():
    # Невірний шифротекст
    invalid_encrypted_text = "abcdef123456"

    # Викликаємо ендпоінт для дешифрування
    response = client.post("/lab4/decrypt_string", data={"encrypted_text": invalid_encrypted_text})

    # Перевіряємо статус відповіді
    assert response.status_code == 400, "Статус відповіді не є 400 Bad Request"
    assert response.json()["status"] == "error", "Статус відповіді не позначений як помилка"
    assert response.json()["message"] == "Помилка дешифрування. Перевірте коректність введеного тексту.", "Текст помилки неправильний"


from bs4 import BeautifulSoup
import os

def test_rsa_file():
    # Створюємо тестовий файл
    test_filename = "test_input.txt"
    with open(test_filename, "w") as f:
        f.write("Це тестовий файл для шифрування.")

    # Відкриваємо файл для передачі в UploadFile
    with open(test_filename, "rb") as file:
        response = client.post("/lab4/rsa_file", files={"encrypt_fileRSA": file})

    # Перевіряємо статус відповіді
    assert response.status_code == 200, "Статус відповіді не є 200 OK"

    # Парсимо HTML-відповідь
    soup = BeautifulSoup(response.text, "html.parser")

    # Перевіряємо, чи в шаблоні є повідомлення про успішне шифрування
    success_message = soup.find("h3", style="color: green;")
    assert success_message is not None, "Повідомлення про успішне шифрування відсутнє"
    assert success_message.text.strip() == "Файл успішно зашифровано.", "Неправильне повідомлення про успішне шифрування"

    # Знаходимо час шифрування
    rsa_enc_time = soup.find("h4")
    assert rsa_enc_time is not None, "Час шифрування відсутній у відповіді"
    assert "секунд" in rsa_enc_time.text, "Неправильний формат часу шифрування"

    # Видаляємо тестовий файл
    os.remove(test_filename)



# def test_decrypt_file():
#    # Створюємо тестовий вхідний файл
#    test_filename = "test_input.txt"
#    with open(test_filename, "w") as f:
#        f.write("Це тестовий файл для дешифрування.")
#
#    # Шифруємо файл
#    public_key = load_public_key()
#    encrypted_file_path = encrypt_file(test_filename, public_key)
#
#    # Відкриваємо зашифрований файл для дешифрування
#    with open(encrypted_file_path, "rb") as file:
#        response = client.post("/lab4/decrypt_file", files={"decrypt_fileRSA": file})
#
#    # Перевіряємо статус відповіді
#    assert response.status_code == 200, "Статус відповіді не є 200 OK"
#    assert "Час дешифрування" in response.text, "Дешифрування не виконано успішно"
#
#    # Перевіряємо, чи створений розшифрований файл
#    decrypted_file_path = response.text.split("decrypted_file_path")[1].split('"')[2]
#    assert os.path.exists(decrypted_file_path), "Розшифрований файл не створено"
#
#    # Видаляємо тестові файли
#    os.remove(test_filename)
#    os.remove(encrypted_file_path)
#    os.remove(decrypted_file_path)


def test_download_decrypted_file():
    # Створюємо тестовий розшифрований файл
    decrypted_file_path = "decrypted_test_file.txt"
    with open(decrypted_file_path, "w") as f:
        f.write("Це тестовий розшифрований файл.")

    # Викликаємо ендпоінт для завантаження
    response = client.get(f"/lab4/download_decrypted_file?file_path={decrypted_file_path}")

    # Перевіряємо статус відповіді
    assert response.status_code == 200, "Статус відповіді не є 200 OK"
    assert response.headers["content-type"] == "application/octet-stream", "Тип контенту неправильний"
    assert response.headers["content-disposition"].startswith("attachment"), "Файл не позначено як attachment"

    # Видаляємо тестовий файл
    os.remove(decrypted_file_path)

def test_download_decrypted_file_not_found():
    # Файл, який не існує
    missing_file_path = "non_existent_file.txt"

    # Викликаємо ендпоінт
    response = client.get(f"/lab4/download_decrypted_file?file_path={missing_file_path}")

    # Перевіряємо статус відповіді
    assert response.status_code == 500, "Статус відповіді не є 500 Internal Server Error"
    assert "Помилка при завантаженні файлу" in response.json()["detail"], "Текст помилки неправильний"
