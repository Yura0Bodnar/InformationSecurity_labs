from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import configparser
import multiprocessing
import random
import math
import os
from concurrent.futures import ProcessPoolExecutor

router = APIRouter()

templates = Jinja2Templates(directory="templates")


class LemerGenerator:
    def __init__(self, seed=1, a=48271, c=0, m=2 ** 31):
        self.a = a
        self.c = c
        self.m = m
        self.state = seed
        self.generated_numbers = []

    def next(self):
        """Generates the next number in the sequence."""
        self.state = (self.a * self.state + self.c) % self.m
        self.generated_numbers.append(self.state)
        return self.state

    def get_bytes(self, num_bytes):
        """Generates `num_bytes` worth of random data."""
        result = b''
        while len(result) < num_bytes:
            number = self.next()
            result += number.to_bytes(4, byteorder='big')
        return result[:num_bytes]

    def save_to_file(self, filename):
        """Saves generated numbers to a file."""
        try:
            with open(filename, 'w') as f:
                for num in self.generated_numbers:
                    f.write(f"{num}\n")
        except IOError as e:
            print(f"Error saving file: {e}")

    def find_period(self):
        sequence = self.generated_numbers  # Using the generated numbers
        length = len(sequence)
        for period in range(1, length // 2 + 1):
            if sequence[:period] == sequence[period:2 * period]:
                return period
        return length


def linear_congruential_generator(m, a, c, x0, n):
    sequence = []
    x = x0
    for _ in range(n):
        x = (a * x + c) % m
        sequence.append(x)
    return sequence


def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def cesaro_test_part(sequence_part, sample_size, use_sampling):
    coprime_count = 0
    total_pairs = 0
    n = len(sequence_part)

    if n < 2:
        return 0, 0

    if use_sampling:
        for _ in range(min(sample_size, n * (n - 1) // 2)):
            i, j = random.sample(range(n), 2)
            total_pairs += 1
            if gcd(sequence_part[i], sequence_part[j]) == 1:
                coprime_count += 1
    else:
        for i in range(len(sequence_part)):
            for j in range(i + 1, len(sequence_part)):
                total_pairs += 1
                if gcd(sequence_part[i], sequence_part[j]) == 1:
                    coprime_count += 1

    return coprime_count, total_pairs


def cesaro_test_worker(args):
    return cesaro_test_part(*args)


def cesaro_test_parallel(sequence, num_workers=5, sample_size=100000):
    n = len(sequence)
    chunk_size = n // num_workers
    chunks = [sequence[i:i + chunk_size] for i in range(0, n, chunk_size)]

    coprime_count = 0
    total_pairs = 0

    use_sampling = n >= 100000
    part_sample_size = sample_size // num_workers if use_sampling else 0

    args = [(chunk, part_sample_size, use_sampling) for chunk in chunks]

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = executor.map(cesaro_test_worker, args)

    for count, pairs in results:
        coprime_count += count
        total_pairs += pairs

    probability = coprime_count / total_pairs if total_pairs > 0 else 0
    estimated_pi = math.sqrt(6 / probability) if probability > 0 else 0

    return estimated_pi


def find_period(sequence):
    seen = {}
    for index, number in enumerate(sequence):
        if number in seen:
            return index - seen[number]
        seen[number] = index
    return len(sequence)


def save_results_to_file(sequence_result, pi_lcg_result, pi_random_result, known_pi, filename="results.txt"):
    try:
        with open(filename, "w") as file:
            file.write("The generated sequence of numbers:\n")
            file.write(sequence_result + "\n\n")
            file.write(str(pi_lcg_result) + "\n\n")
            file.write(str(pi_random_result) + "\n\n")
            file.write(str(known_pi) + "\n")
    except Exception as e:
        print(f"Error saving results: {e}")


@router.get("/", response_class=HTMLResponse)
async def read_lab(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/lab1", response_class=HTMLResponse)
async def lab1(request: Request, inputLab1: int = Form(...)):
    config = configparser.ConfigParser()
    config.read("config.ini")
    m = int(config["LCG"]["m"])
    a = int(config["LCG"]["a"])
    c = int(config["LCG"]["c"])
    x0 = int(config["LCG"]["x0"])

    try:
        if inputLab1 > 1500000:
            return templates.TemplateResponse("index.html", {"request": request,
                                                             "outputLab1": "Надто велике число, введіть менше n."})
        elif inputLab1 <= 0:
            return templates.TemplateResponse("index.html", {"request": request,
                                                             "outputLab1": "Число має бути більше нуля. Введіть інше значення."})
        elif 0 < inputLab1 < 20:
            return templates.TemplateResponse("index.html", {"request": request,
                                                             "outputLab1": "Замале n. Введіть більше число."})

        sequence = linear_congruential_generator(m, a, c, x0, inputLab1)
        sequence_result = " ".join(map(str, sequence))

        period = find_period(sequence)

        estimated_pi_lcg = cesaro_test_parallel(sequence)
        pi_lcg_result = f"Estimation of the Pi number using LCG: {estimated_pi_lcg}"

        random_sequence = [random.randint(1, m) for _ in range(inputLab1)]
        estimated_pi_random = cesaro_test_parallel(random_sequence)
        pi_random_result = f"Estimating the number Pi using a system generator: {estimated_pi_random}"

        known_pi = f"The value of Pi is known: {math.pi}"

        save_results_to_file(sequence_result, pi_lcg_result, pi_random_result, known_pi)

        num_cores = multiprocessing.cpu_count()
        print(f"Кількість процесорних ядер: {num_cores}")

        return templates.TemplateResponse("index.html", {
            "request": request,
            "outputLab1": sequence_result,
            "outputLab1_2": period,
            "chesaro": estimated_pi_lcg,
            "random_sequence": estimated_pi_random,
            "pi": known_pi
        })

    except ValueError:
        return templates.TemplateResponse("index.html", {"request": request,
                                                         "outputLab1": "Помилка: n має бути цілим числом. Спробуйте ще раз."})


@router.get("/download_results", response_class=FileResponse)
async def download_results():
    filename = "results.txt"
    if os.path.exists(filename):
        return FileResponse(path=filename, media_type='application/octet-stream', filename=filename)
    return {"status": "error", "message": "Файл не знайдено."}
