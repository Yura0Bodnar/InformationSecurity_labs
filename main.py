from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers import lab1, lab2, lab3, lab4, lab5
import configparser
import math
import random
from concurrent.futures import ProcessPoolExecutor

app = FastAPI()

# Підключення шаблонів та статичних файлів
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Підключення роутерів
app.include_router(lab1.router)
app.include_router(lab2.router)
app.include_router(lab3.router)
app.include_router(lab4.router)
app.include_router(lab5.router)


# Лінійний конгруентний генератор
def linear_congruential_generator(m, a, c, x0, n):
    sequence = []
    x = x0
    for _ in range(n):
        x = (a * x + c) % m
        sequence.append(x)
    return sequence


# Пошук найбільшого спільного дільника
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


# Частина тесту Чезаро
def cesaro_test_part(sequence_part):
    coprime_count = 0
    total_pairs = 0
    for i in range(len(sequence_part)):
        for j in range(i + 1, len(sequence_part)):
            total_pairs += 1
            if gcd(sequence_part[i], sequence_part[j]) == 1:
                coprime_count += 1
    return coprime_count, total_pairs


# Паралельний тест Чезаро
def cesaro_test_parallel(sequence, num_workers=4):
    chunk_size = len(sequence) // num_workers
    chunks = [sequence[i:i + chunk_size] for i in range(0, len(sequence), chunk_size)]

    coprime_count = 0
    total_pairs = 0

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = executor.map(cesaro_test_part, chunks)

    for count, pairs in results:
        coprime_count += count
        total_pairs += pairs

    probability = coprime_count / total_pairs if total_pairs > 0 else 0
    estimated_pi = math.sqrt(6 / probability) if probability > 0 else 0

    return estimated_pi


# Пошук періоду послідовності
def find_period(sequence):
    seen = {}
    for index, number in enumerate(sequence):
        if number in seen:
            return index - seen[number]
        seen[number] = index
    return len(sequence)


# Збереження результатів у файл
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


@app.get("/", response_class=HTMLResponse)
async def read_lab(request: Request):
    """
    Головна сторінка.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/lab1", response_class=HTMLResponse)
async def lab1(request: Request, inputLab1: int = Form(...)):
    """
    Лабораторна робота 1: Лінійний конгруентний генератор.
    """
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
