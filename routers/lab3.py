from fastapi import APIRouter, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
import struct
import os
from fastapi.responses import HTMLResponse
from fastapi import Request
from routers.lab1 import LemerGenerator  # Імпортуємо генератор Лемера для IV
from routers.lab2 import MD5_a  # Імпортуємо MD5 для генерації ключів


router = APIRouter()

templates = Jinja2Templates(directory="templates")


class RC5CBCPad:
    def __init__(self, key, word_size=32, num_rounds=20):
        self.block_size = 8  # 64 біт (8 байт) на блок
        self.word_size = word_size
        self.num_rounds = num_rounds
        self.key = self._pad_key(key, 16)  # Довжина ключа - 16 байт

    def _pad_key(self, key, block_size):
        key_len = len(key)
        if key_len >= block_size:
            return key[:block_size]
        else:
            return key + b'\x00' * (block_size - key_len)

    def _xor_bytes(self, a, b):
        return bytes(x ^ y for x, y in zip(a, b))

    def _pad_data(self, data):
        padding_len = self.block_size - len(data) % self.block_size
        padding = bytes([padding_len] * padding_len)
        return data + padding

    def _unpad_data(self, data):
        padding_len = data[-1]
        if padding_len < 1 or padding_len > self.block_size:
            raise ValueError("Invalid padding")
        if data[-padding_len:] != bytes([padding_len] * padding_len):
            raise ValueError("Invalid padding")
        return data[:-padding_len]

    def _split_blocks(self, data):
        return [data[i:i + self.block_size] for i in range(0, len(data), self.block_size)]

    def _rc5_encrypt_block(self, block):
        A, B = struct.unpack('!II', block)  # 2 слова по 32 біти
        round_keys = self._expand_key()

        for i in range(self.num_rounds):
            A = (A + round_keys[2 * i]) & ((1 << self.word_size) - 1)
            B = (B + round_keys[2 * i + 1]) & ((1 << self.word_size) - 1)
            A ^= B
            A = (A << (B % self.word_size)) | (A >> (self.word_size - (B % self.word_size)))
            A &= ((1 << self.word_size) - 1)
            B ^= A
            B = (B << (A % self.word_size)) | (B >> (self.word_size - (A % self.word_size)))
            B &= ((1 << self.word_size) - 1)

        return struct.pack('!II', A, B)

    def _rc5_decrypt_block(self, block):
        A, B = struct.unpack('!II', block)  # 2 слова по 32 біти
        round_keys = self._expand_key()

        for i in range(self.num_rounds - 1, -1, -1):
            B = (B >> (A % self.word_size)) | (B << (self.word_size - (A % self.word_size)))
            B &= ((1 << self.word_size) - 1)
            B ^= A
            A = (A >> (B % self.word_size)) | (A << (self.word_size - (B % self.word_size)))
            A &= ((1 << self.word_size) - 1)
            A ^= B
            B = (B - round_keys[2 * i + 1]) & ((1 << self.word_size) - 1)
            A = (A - round_keys[2 * i]) & ((1 << self.word_size) - 1)

        return struct.pack('!II', A, B)

    def _expand_key(self):
        P = 0xB7E15163
        Q = 0x9E3779B9
        round_keys = [(P + (i * Q)) & ((1 << self.word_size) - 1) for i in range(2 * (self.num_rounds + 1))]

        key_words = list(struct.unpack('!' + 'I' * (len(self.key) // 4), self.key))  # Кожне слово - 32 біти
        i = j = 0
        A = B = 0

        for _ in range(3 * max(len(key_words), 2 * (self.num_rounds + 1))):
            A = round_keys[i] = (round_keys[i] + A + B) & ((1 << self.word_size) - 1)
            B = key_words[j] = (key_words[j] + A + B) & ((1 << self.word_size) - 1)
            i = (i + 1) % (2 * (self.num_rounds + 1))
            j = (j + 1) % len(key_words)

        return round_keys

    def generate_seed(self):
        return int.from_bytes(os.urandom(4), byteorder='big')

    # Методи для роботи з файлами (Encryption, Decryption)
    def encrypt_file(self, input_filename, output_filename):
        seed = self.generate_seed()
        lemer_generator = LemerGenerator(seed)
        iv = lemer_generator.get_bytes(self.block_size)

        with open(input_filename, 'rb') as infile:
            plaintext = infile.read()

        encrypted_data = self.encrypt_file_mode(plaintext, iv)

        with open(output_filename, 'wb') as outfile:
            outfile.write(encrypted_data)

    def decrypt_file(self, input_filename, output_filename):
        with open(input_filename, 'rb') as infile:
            iv_ciphertext = infile.read()

        iv = iv_ciphertext[:self.block_size]
        ciphertext = iv_ciphertext[self.block_size:]

        decrypted_data = self.decrypt_file_mode(ciphertext, iv)

        with open(output_filename, 'wb') as outfile:
            outfile.write(decrypted_data)

    # Методи для роботи з консольним введенням (Encryption, Decryption)
    def encrypt_console(self, plaintext, iv):
        plaintext = self._pad_data(plaintext)
        blocks = self._split_blocks(plaintext)
        ciphertext = b''
        prev_block = iv

        for block in blocks:
            block = self._xor_bytes(block, prev_block)
            cipher = self._rc5_encrypt_block(block)
            ciphertext += cipher
            prev_block = cipher

        return iv + ciphertext

    def decrypt_console(self, ciphertext, iv):
        blocks = self._split_blocks(ciphertext[len(iv):])
        plaintext = b''
        prev_block = iv

        for block in blocks:
            decrypted_block = self._rc5_decrypt_block(block)
            plaintext += self._xor_bytes(decrypted_block, prev_block)
            prev_block = block

        plaintext = self._unpad_data(plaintext)
        return plaintext

    # Функції для шифрування та дешифрування для файлів
    def encrypt_file_mode(self, plaintext, iv):
        plaintext = self._pad_data(plaintext)
        blocks = self._split_blocks(plaintext)
        ciphertext = b''
        prev_block = iv

        for block in blocks:
            block = self._xor_bytes(block, prev_block)
            cipher = self._rc5_encrypt_block(block)
            ciphertext += cipher
            prev_block = cipher

        return iv + ciphertext

    def decrypt_file_mode(self, ciphertext, iv):
        blocks = self._split_blocks(ciphertext)
        plaintext = b''
        prev_block = iv

        for block in blocks:
            decrypted_block = self._rc5_decrypt_block(block)
            plaintext += self._xor_bytes(decrypted_block, prev_block)
            prev_block = block

        plaintext = self._unpad_data(plaintext)
        return plaintext


# Зберігаємо пароль
saved_password = None


@router.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": ""})


@router.post("/lab3/set_password")
async def set_password(password: str = Form(...)):
    global saved_password
    saved_password = password
    return {"message": "Password saved successfully."}


@router.post("/lab3/encrypt_file")
async def encrypt_file(request: Request, encrypt_file: UploadFile = File(...)):
    if not saved_password:
        return templates.TemplateResponse("index.html", {"request": request, "message": "No password saved!"})

    file_location = f"files/{encrypt_file.filename}"
    with open(file_location, "wb") as file:
        file.write(await encrypt_file.read())

    # Виконуємо шифрування
    md5_service = MD5_a()
    key = md5_service.hexdigest().encode('utf-8')[:16]  # Тільки 16 байтів
    rc5 = RC5CBCPad(key, word_size=32, num_rounds=20)

    encrypted_file_location = file_location + ".enc"
    rc5.encrypt_file(file_location, encrypted_file_location)

    return templates.TemplateResponse("index.html",
                                      {"request": request, "message": f"File encrypted: {encrypted_file_location}"})


@router.post("/lab3/decrypt_file")
async def decrypt_file(request: Request, decrypt_file: UploadFile = File(...), password: str = Form(...)):
    global saved_password
    if saved_password != password:
        return templates.TemplateResponse("index.html", {"request": request, "message": "Incorrect password!"})

    file_location = f"files/{decrypt_file.filename}"
    with open(file_location, "wb") as file:
        file.write(await decrypt_file.read())

    # Виконуємо дешифрування
    md5_service = MD5_a()
    key = md5_service.hexdigest().encode('utf-8')[:16]  # Тільки 16 байтів
    rc5 = RC5CBCPad(key, word_size=32, num_rounds=20)

    decrypted_file_location = file_location.replace(".enc", "_decrypted.txt")
    rc5.decrypt_file(file_location, decrypted_file_location)

    return templates.TemplateResponse("index.html",
                                      {"request": request, "message": f"File decrypted: {decrypted_file_location}"})


@router.post("/lab3/encrypt_text")
async def encrypt_text(request: Request, input_text: str = Form(...)):
    if not saved_password:
        return templates.TemplateResponse("index.html", {"request": request, "message": "No password saved!"})

    # Виконуємо шифрування тексту
    md5_service = MD5_a()
    key = md5_service.hexdigest().encode('utf-8')[:16]
    rc5 = RC5CBCPad(key, word_size=32, num_rounds=20)

    seed = rc5.generate_seed()
    lemer_generator = LemerGenerator(seed)
    iv = lemer_generator.get_bytes(8)

    ciphertext = rc5.encrypt_console(input_text.encode('utf-8'), iv)
    encrypted_text = (iv + ciphertext).hex()

    return templates.TemplateResponse("index.html",
                                      {"request": request, "message": f"Encrypted text: {encrypted_text}"})


@router.post("/lab3/decrypt_text")
async def decrypt_text(request: Request, input_text: str = Form(...), password: str = Form(...)):
    global saved_password
    if saved_password != password:
        return templates.TemplateResponse("index.html", {"request": request, "message": "Incorrect password!"})

    # Виконуємо дешифрування тексту
    md5_service = MD5_a()
    key = md5_service.hexdigest().encode('utf-8')[:16]
    rc5 = RC5CBCPad(key, word_size=32, num_rounds=20)

    try:
        ciphertext = bytes.fromhex(input_text)
        iv = ciphertext[:8]
        ciphertext_body = ciphertext[8:]
        decrypted_text = rc5.decrypt_console(ciphertext_body, iv).decode('utf-8')
    except ValueError as e:
        return templates.TemplateResponse("index.html", {"request": request, "message": f"Decryption failed: {e}"})

    return templates.TemplateResponse("index.html",
                                      {"request": request, "message": f"Decrypted text: {decrypted_text}"})
