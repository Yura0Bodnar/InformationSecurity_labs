from fastapi import APIRouter, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import struct
import math

router = APIRouter()

templates = Jinja2Templates(directory="templates")


def left_rotate(x, c):
    return (x << c) & 0xFFFFFFFF | (x >> (32 - c))


# Основний клас MD5
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


# Функція для хешування файлу
async def md5_file(file: UploadFile) -> str:
    md5 = MD5()
    while chunk := await file.read(64):
        md5.update(chunk)
    return md5.hexdigest()


# Перевірка цілісності файлу
async def verify_file_integrity(file: UploadFile, hash_file: UploadFile) -> bool:
    computed_hash = await md5_file(file)
    original_hash = await hash_file.read()
    return computed_hash == original_hash.decode().strip()


# Маршрут для хешування файлу
@router.post("/lab2/md5_file", response_class=HTMLResponse)
async def hash_file(request: Request, file: UploadFile = File(...)):
    hash_result = await md5_file(file)
    return templates.TemplateResponse("index.html", {"request": request, "file_hash": hash_result})


# Маршрут для перевірки цілісності файлу
@router.post("/lab2/verify_file", response_class=HTMLResponse)
async def verify_file(request: Request, file: UploadFile = File(...), hash_file: UploadFile = File(...)):
    is_intact = await verify_file_integrity(file, hash_file)
    return templates.TemplateResponse("index.html", {"request": request, "is_intact": is_intact})
