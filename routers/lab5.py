from fastapi import APIRouter, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
import binascii
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Helper functions for DSA
class DigitalSignature:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_keys(self):
        self.private_key = dsa.generate_private_key(key_size=2048)
        self.public_key = self.private_key.public_key()

    def save_key_to_file(self, key, filename, is_private=True):
        if is_private:
            pem = key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            pem = key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        with open(filename, 'wb') as f:
            f.write(pem)

    def load_key_from_file(self, filename, is_private=True):
        with open(filename, 'rb') as f:
            key_data = f.read()
        if is_private:
            self.private_key = serialization.load_pem_private_key(key_data, password=None)
        else:
            self.public_key = serialization.load_pem_public_key(key_data)

    def sign_data(self, data):
        signature = self.private_key.sign(data, hashes.SHA256())
        return binascii.hexlify(signature).decode()

    def verify_signature(self, data, signature):
        try:
            signature = binascii.unhexlify(signature)
            self.public_key.verify(signature, data, hashes.SHA256())
            return True
        except InvalidSignature:
            return False


# Initialize DSA helper
ds = DigitalSignature()


@router.post("/lab5/generate_keys", response_class=HTMLResponse)
async def generate_keys(request: Request):
    """
    Генерація ключів DSA.
    """
    ds.generate_keys()
    ds.save_key_to_file(ds.private_key, "dsa_private_key.pem")
    ds.save_key_to_file(ds.public_key, "dsa_public_key.pem", is_private=False)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "key_generation_result": "DSA ключі згенеровані та збережені у файли.",
        "show_lab5": True
    })


string_result_dsa = ""  # Глобальна змінна для зберігання підпису
global_input_text_dsa = ""


@router.post("/lab5/sign_data", response_class=HTMLResponse)
async def sign_data(request: Request, input_text_dsa: str = Form(...)):
    """
    Ендпоінт для підпису даних.
    """
    global string_result_dsa, global_input_text_dsa  # Оголошуємо змінні як глобальні

    global_input_text_dsa = input_text_dsa

    # Завантаження приватного ключа
    ds.load_key_from_file("dsa_private_key.pem")

    # Генерація підпису
    string_result_dsa = ds.sign_data(input_text_dsa.encode())

    # Повертаємо шаблон із результатом підпису
    return templates.TemplateResponse("index.html", {
        "request": request,
        "string_result_dsa": string_result_dsa,
        "input_text_dsa": input_text_dsa,
        "show_lab5": True
    })


@router.get("/lab5/download_signature", response_class=FileResponse)
async def download_signature():
    """
    Ендпоінт для завантаження файлу з підписом.
    """
    file_path = "signature.txt"  # Шлях до тимчасового файлу
    with open(file_path, "w") as file:
        file.write(string_result_dsa)  # Записуємо підпис у файл

    return FileResponse(file_path, media_type="text/plain", filename="signature.txt")


@router.post("/lab5/verify_signature", response_class=HTMLResponse)
async def verify_signature(signature: str = Form(...)):
    """
    Ендпоінт для перевірки підпису. Повертає лише результат перевірки.
    """
    try:
        global global_input_text_dsa

        if not global_input_text_dsa:
            raise ValueError("Глобальний текст для підпису не встановлений. Спочатку виконайте підпис.")

        # Завантаження публічного ключа
        ds.load_key_from_file("dsa_public_key.pem", is_private=False)

        # Перевірка підпису
        is_valid = ds.verify_signature(global_input_text_dsa.encode(), signature)
        message = "Підпис дійсний." if is_valid else "Підпис недійсний."
    except Exception as e:
        message = f"Помилка перевірки: {str(e)}"

    # Повертаємо мінімальний HTML
    return HTMLResponse(content=f"<h4>{message}</h4>")


last_signed_file_path = None


@router.post("/lab5/sign_file", response_class=HTMLResponse)
async def sign_file(request: Request, file: UploadFile = File(...)):
    """
    Ендпоінт для підпису файлу.
    """
    try:
        global last_signed_file_path  # Зберігаємо шлях до підписаного файлу

        ds.load_key_from_file("dsa_private_key.pem")
        file_data = await file.read()

        if not file_data:
            raise ValueError("Файл порожній. Немає даних для підпису.")

        signature = ds.sign_data(file_data)

        # Отримуємо назву файлу без розширення
        file_name_without_extension, _ = os.path.splitext(file.filename)

        signature_file = f"{file_name_without_extension}_signature.enc"
        last_signed_file_path = f"./{file.filename}"  # Зберігаємо шлях до файлу
        with open(last_signed_file_path, "wb") as f:
            f.write(file_data)

        with open(signature_file, "w") as f:
            f.write(signature)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "file_sign_result": f"Файл успішно підписано. Підпис збережено у '{signature_file}'.",
            "show_lab5": True
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error_message": f"Помилка підпису: {str(e)}",
            "show_lab5": True
        })


@router.post("/lab5/verify_file", response_class=HTMLResponse)
async def verify_file(request: Request, signature_file: UploadFile = File(...)):
    """
    Ендпоінт для перевірки підпису файлу. Основний файл використовується із попереднього ендпоінта.
    """
    try:
        global last_signed_file_path  # Використовуємо глобальну змінну для останнього підписаного файлу

        if not last_signed_file_path or not os.path.exists(last_signed_file_path):
            raise ValueError("Файл для перевірки підпису не знайдено. Спочатку виконайте підпис файлу.")

        # Завантаження публічного ключа
        ds.load_key_from_file("dsa_public_key.pem", is_private=False)

        # Читання підписаного файлу та підпису
        with open(last_signed_file_path, "rb") as f:
            file_data = f.read()

        signature = await signature_file.read()

        if not file_data or not signature:
            raise ValueError("Файл або підпис порожні.")

        # Перевірка підпису
        is_valid = ds.verify_signature(file_data, signature.decode())

        return templates.TemplateResponse("index.html", {
            "request": request,
            "file_verify_result": "Підпис дійсний." if is_valid else "Підпис недійсний.",
            "show_lab5": True
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error_message": f"Помилка перевірки підпису: {str(e)}",
            "show_lab5": True
        })
