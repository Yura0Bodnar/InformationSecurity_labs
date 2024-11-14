from fastapi import APIRouter, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os
import time

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def generate_keys():
    """Генерація ключів RSA."""
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    with open("private_key.pem", "wb") as priv_file:
        priv_file.write(private_key)
    with open("public_key.pem", "wb") as pub_file:
        pub_file.write(public_key)

    return "Ключі згенеровані та збережені у файли."


def load_private_key():
    """Завантаження приватного ключа з файлу."""
    with open("private_key.pem", "rb") as priv_file:
        private_key = RSA.import_key(priv_file.read())
    return private_key


def load_public_key():
    """Завантаження публічного ключа з файлу."""
    with open("public_key.pem", "rb") as pub_file:
        public_key = RSA.import_key(pub_file.read())
    return public_key


def encrypt_message(message: str, public_key):
    """Шифрування повідомлення."""
    cipher = PKCS1_OAEP.new(public_key)
    encrypted_data = cipher.encrypt(message.encode())
    return encrypted_data


def decrypt_message(encrypted_data: bytes, private_key):
    """Розшифрування повідомлення."""
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data.decode()


BLOCK_SIZE = 214


async def encrypt_file(input_file: UploadFile, public_key) -> str:
    """Шифрування файлу по блоках з використанням RSA."""
    try:
        # Зчитуємо дані з файлу
        file_data = await input_file.read()

        # Перевіряємо, чи файл не порожній
        if not file_data:
            raise ValueError("Файл порожній. Немає даних для шифрування.")

        # Ініціалізуємо шифратор RSA
        cipher = PKCS1_OAEP.new(public_key)

        # Шифруємо файл по блоках
        encrypted_data = b""
        for i in range(0, len(file_data), BLOCK_SIZE):
            block = file_data[i:i + BLOCK_SIZE]
            encrypted_block = cipher.encrypt(block)
            encrypted_data += encrypted_block

        # Формуємо шлях до вихідного зашифрованого файлу
        sanitized_filename = input_file.filename.replace(" ", "_")  # Уникаємо пробілів
        # Видаляємо розширення файлу
        file_name_without_extension, file_extension = os.path.splitext(sanitized_filename)
        # Формуємо шлях до файлу з новим розширенням .enc
        output_file_path = f"encrypted_{file_name_without_extension}.enc"

        # Записуємо зашифровані дані у файл
        with open(output_file_path, "wb") as enc_file:
            enc_file.write(encrypted_data)

        return output_file_path
    except Exception as e:
        raise RuntimeError(f"Помилка під час шифрування файлу: {e}")


async def decrypt_file(encrypted_file: UploadFile, private_key) -> str:
    """Розшифрування файлу по блоках з використанням RSA."""
    try:
        # Зчитуємо зашифровані дані з файлу
        encrypted_data = await encrypted_file.read()

        # Ініціалізуємо шифратор RSA для дешифрування
        cipher = PKCS1_OAEP.new(private_key)

        # Дешифруємо файл по блоках
        decrypted_data = b""
        block_size = private_key.size_in_bytes()
        for i in range(0, len(encrypted_data), block_size):
            encrypted_block = encrypted_data[i:i + block_size]
            decrypted_block = cipher.decrypt(encrypted_block)
            decrypted_data += decrypted_block

        # Формуємо шлях до розшифрованого файлу
        decrypted_file_path = f"decrypted_{encrypted_file.filename}"

        # Відкриваємо файл для запису бінарних даних
        with open(decrypted_file_path, "wb") as dec_file:
            dec_file.write(decrypted_data)

        return decrypted_file_path
    except Exception as e:
        raise RuntimeError(f"Помилка під час дешифрування файлу: {e}")


@router.post("/lab4/generate_key", response_class=HTMLResponse)
async def generate_key(request: Request):
    """Генерація RSA ключів."""
    generate_keys()  # Викликаємо функцію для генерації ключів
    return templates.TemplateResponse("index.html", {
        "request": request,
        "key_generation_result": "Ключі успішно згенеровані та збережені у файли.",
        "show_lab4": True
    })


@router.post("/lab4/rsa_string", response_class=HTMLResponse)
async def rsa_hash_string(request: Request, input_text_rsa: str = Form(...)):
    public_key = load_public_key()
    encrypted_message = encrypt_message(input_text_rsa, public_key)

    # Показуємо результат і можливість завантаження
    return templates.TemplateResponse("index.html", {
        "request": request,
        "string_result_rsa": encrypted_message.hex(),
        "input_text_rsa": input_text_rsa,
        "show_lab4": True
    })


@router.get("/lab4/download_results", response_class=FileResponse)
async def download_results():
    filename = "result_rsa.txt"
    if os.path.exists(filename):
        return FileResponse(path=filename, media_type="application/octet-stream", filename=filename)
    else:
        raise HTTPException(status_code=404, detail="Файл не знайдено.")


@router.post("/lab4/decrypt_string", response_class=JSONResponse)
async def decrypt_rsa_string(encrypted_text: str = Form(...)):
    try:
        private_key = load_private_key()

        # Перетворення шифрованого тексту з hex у bytes
        encrypted_data = bytes.fromhex(encrypted_text)
        decrypted_message = decrypt_message(encrypted_data, private_key)

        return JSONResponse(content={"status": "success", "decrypted_result": decrypted_message})
    except ValueError:
        return JSONResponse(content={"status": "error", "message": "Помилка дешифрування. Перевірте коректність введеного тексту."}, status_code=400)


@router.post("/lab4/rsa_file", response_class=HTMLResponse)
async def rsa_file(request: Request, encrypt_fileRSA: UploadFile = File(...)):
    try:
        start_time = time.time()

        public_key = load_public_key()
        encrypted_file_path = await encrypt_file(encrypt_fileRSA, public_key)

        # Обчислення часу виконання
        end_time = time.time()
        rsa_enc_time = end_time - start_time

        # Повертаємо повідомлення про успіх у шаблон
        return templates.TemplateResponse("index.html", {
            "request": request,
            "file_hash_rsa": "Файл успішно зашифровано.",
            "encrypted_file_path": encrypted_file_path,
            "rsa_enc_time": f"Час шифрування: {rsa_enc_time:.2f} секунд.",
            "show_lab4": True
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error_message": f"Помилка шифрування: {str(e)}",
            "show_lab4": True
        })


@router.post("/lab4/decrypt_file", response_class=HTMLResponse)
async def decrypt_file_route(request: Request, decrypt_fileRSA: UploadFile = File(...)):
    try:
        start_time = time.time()

        private_key = load_private_key()
        decrypted_file_path = await decrypt_file(decrypt_fileRSA, private_key)

        # Обчислення часу виконання
        end_time = time.time()
        decryption_time = end_time - start_time

        # Повертаємо результат у HTML-шаблон
        return templates.TemplateResponse("index.html", {
            "request": request,
            "decrypted_file_path": decrypted_file_path,
            "decryption_time": f"Час дешифрування: {decryption_time:.2f} секунд.",
            "show_lab4": True
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error_message": f"Помилка дешифрування: {str(e)}",
            "show_lab4": True
        })


@router.get("/lab4/download_decrypted_file", response_class=FileResponse)
async def download_decrypted_file(file_path: str):
    """
    Ендпоінт для завантаження розшифрованого файлу.
    """
    try:
        # Перевіряємо, чи файл існує
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не знайдено.")

        # Повертаємо файл для завантаження
        return FileResponse(path=file_path, media_type="application/octet-stream", filename=os.path.basename(file_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при завантаженні файлу: {e}")
