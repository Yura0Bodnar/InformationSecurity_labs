from fastapi import APIRouter, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
import struct
import math
import os
import json
import pandas as pd
from PyPDF2 import PdfReader
import hashlib

router = APIRouter()


def save_results_to_file(hash_result, filename: str):
    try:
        with open(filename, "w") as file:
            file.write("Hash code:\n")
            file.write(hash_result + "\n\n")
    except Exception as e:
        print(f"Error saving results: {e}")


def left_rotate(x, c):
    return (x << c) & 0xFFFFFFFF | (x >> (32 - c))


class MD5:
    def __init__(self):
        self.A = 0x67452301
        self.B = 0xEFCDAB89
        self.C = 0x98BADCFE
        self.D = 0x10325476
        self.K = [int(abs(math.sin(i + 1)) * (2 ** 32)) & 0xFFFFFFFF for i in range(64)]
        self.shifts = [7, 12, 17, 22] * 4 + [5, 9, 14, 20] * 4 + [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4

    def md5_padding(self, message):
        original_length = len(message) * 8
        message += b'\x80'
        while (len(message) * 8) % 512 != 448:
            message += b'\x00'
        message += struct.pack('<Q', original_length)
        return message

    def process_block(self, block):
        X = list(struct.unpack('<16I', block))
        A, B, C, D = self.A, self.B, self.C, self.D

        for i in range(64):
            if i < 16:
                F = (B & C) | (~B & D)
                g = i
            elif i < 32:
                F = (D & B) | (~D & C)
                g = (5 * i + 1) % 16
            elif i < 48:
                F = B ^ C ^ D
                g = (3 * i + 5) % 16
            else:
                F = C ^ (B | ~D)
                g = (7 * i) % 16

            F = (F + A + self.K[i] + X[g]) & 0xFFFFFFFF
            A, D, C, B = D, C, B, (B + left_rotate(F, self.shifts[i])) & 0xFFFFFFFF

        self.A = (self.A + A) & 0xFFFFFFFF
        self.B = (self.B + B) & 0xFFFFFFFF
        self.C = (self.C + C) & 0xFFFFFFFF
        self.D = (self.D + D) & 0xFFFFFFFF

    def update(self, message):
        message = self.md5_padding(message)
        for i in range(0, len(message), 64):
            self.process_block(message[i:i + 64])

    def hexdigest(self):
        return ''.join([struct.pack('<I', x).hex() for x in [self.A, self.B, self.C, self.D]])


async def md5_file(file: UploadFile) -> str:
    md5 = hashlib.md5()
    while chunk := await file.read(8192):
        md5.update(chunk)
    return md5.hexdigest()


@router.post("/lab2/md5_string", response_class=JSONResponse)
async def hash_string(input_string: str = Form(...)):
    md5 = MD5()
    md5.update(input_string.encode())
    hash_result = md5.hexdigest()

    # Зберігаємо результат у файл
    save_results_to_file(hash_result, "result_md5.txt")

    return {"string_result": hash_result, "input_string": input_string}


@router.get("/download_results_lab2", response_class=JSONResponse)
async def download_results():
    filename = "result_md5.txt"
    if os.path.exists(filename):
        with open(filename, "r") as file:
            content = file.read()
        return {"status": "success", "content": content}
    return {"status": "error", "message": "Файл не знайдено."}


@router.post("/lab2/process_file", response_class=JSONResponse)
async def process_file(file: UploadFile = File(...)):
    file_hash = await md5_file(file)

    # Переміщуємо вказівник файлу на початок після хешування
    file.file.seek(0)

    # Аналізуємо вміст файлу
    try:
        if file.filename.endswith(".txt"):
            content = await read_txt(file)
        elif file.filename.endswith(".pdf"):
            content = await read_pdf(file)
        elif file.filename.endswith(".csv"):
            content = await read_csv(file)
        elif file.filename.endswith(".json"):
            content = await read_json(file)
        else:
            return {"status": "error", "message": "Unsupported file format"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {"file_hash": file_hash, "content": content, "filename": file.filename}


async def verify_file_integrity(computed_hash: str, hash_file: UploadFile) -> bool:
    original_hash = await hash_file.read()
    return computed_hash == original_hash.decode().strip()


@router.post("/lab2/verify_file", response_class=JSONResponse)
async def verify_file(file_hash: str = Form(...), hash_file: UploadFile = File(...)):
    is_intact = await verify_file_integrity(file_hash, hash_file)
    return {"file_hash": file_hash, "is_intact": is_intact}


async def read_txt(file: UploadFile) -> str:
    content = await file.read()
    return content.decode("utf-8")


async def read_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


async def read_csv(file: UploadFile) -> str:
    df = pd.read_csv(file.file, skiprows=1, header=None)
    return str(df.iloc[0, 0])


async def read_json(file: UploadFile) -> str:
    content = await file.read()
    json_data = json.loads(content.decode("utf-8"))
    return str(json_data.get("text", ""))
