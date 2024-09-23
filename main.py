from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import configparser
import math
import random

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


def linear_congruential_generator(m, a, c, x0, n):
    sequence = []
    x = x0
    for _ in range(n):
        x = (a * x + c) % m
        sequence.append(x)
    return sequence


def gcd(a, b):
    """Функція для обчислення найбільшого спільного дільника (НСД) за допомогою алгоритму Евкліда."""
    while b != 0:
        a, b = b, a % b
    return a


def cesaro_test(sequence):
    """Функція для тестування генератора на основі теореми Чезаро і визначення значення π."""
    coprime_count = 0
    total_pairs = 0

    # Проходимо по всіх парах чисел у послідовності
    for i in range(len(sequence)):
        for j in range(i + 1, len(sequence)):
            total_pairs += 1
            if gcd(sequence[i], sequence[j]) == 1:
                coprime_count += 1

    # Ймовірність того, що два випадкові числа є взаємно простими
    probability = coprime_count / total_pairs

    # Оцінка числа π за формулою теореми Чезаро
    estimated_pi = math.sqrt(6 / probability)

    return estimated_pi


def find_period(sequence):
    seen = {}
    for index, number in enumerate(sequence):
        if number in seen:
            return index - seen[number]
        seen[number] = index
    return len(sequence)


def save_results_to_file(sequence_result, pi_lcg_result, pi_random_result, known_pi, filename="results.txt"):
    """Функція для збереження результатів у файл."""
    with open(filename, "w") as file:
        file.write("Згенерована послідовність чисел:\n")
        file.write(sequence_result + "\n\n")
        file.write("Оцінка числа π з використанням ЛКГ:\n")
        file.write(pi_lcg_result + "\n\n")
        file.write("Оцінка числа π з використанням системного генератора:\n")
        file.write(pi_random_result + "\n\n")
        file.write("Відоме значення числа π:\n")
        file.write(known_pi + "\n")


@app.get("/", response_class=HTMLResponse)
async def read_lab(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def read_lab(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/lab1", response_class=HTMLResponse)
async def lab1(request: Request, inputLab1: int = Form(...)):
    config = configparser.ConfigParser()
    config.read("config.ini")
    m = int(config["LCG"]["m"])
    a = int(config["LCG"]["a"])
    c = int(config["LCG"]["c"])
    x0 = int(config["LCG"]["x0"])

    try:
        if inputLab1 > 1500000:
            return templates.TemplateResponse("index.html", {"request": request, "outputLab1": "Надто велике число, введіть менше n."})
        elif inputLab1 <= 0:
            return templates.TemplateResponse("index.html", {"request": request, "outputLab1": "Число має бути більше нуля. Введіть інше значення."})

        # Генерація послідовності псевдовипадкових чисел
        sequence = linear_congruential_generator(m, a, c, x0, inputLab1)
        sequence_result = " ".join(map(str, sequence))

        # Знаходження періоду послідовності
        period = find_period(sequence)

        # Оцінка числа π з використанням теореми Чезаро (ЛКГ)
        estimated_pi_lcg = cesaro_test(sequence)
        pi_lcg_result = f"Оцінка числа π з використанням ЛКГ: {estimated_pi_lcg}"

        # Тестування генератора з системної бібліотеки random
        random_sequence = [random.randint(1, m) for _ in range(inputLab1)]
        estimated_pi_random = cesaro_test(random_sequence)
        pi_random_result = f"Оцінка числа π з використанням системного генератора: {estimated_pi_random}"

        # Порівняння з реальним значенням π
        known_pi = f"Відоме значення числа π: {math.pi}"

        # Зберігаємо результати у файл
        save_results_to_file(sequence_result, pi_lcg_result, pi_random_result, known_pi)

        # Об'єднуємо результати для відображення
        combined_result = f"{pi_lcg_result}<br>{pi_random_result}<br>{known_pi}"

        return templates.TemplateResponse("index.html", {
            "request": request,
            "outputLab1": sequence_result,  # Згенерована послідовність
            "outputLab1_2": period,  # Період послідовності
            "outputLab1_3": combined_result  # Результати оцінки числа π
        })

    except ValueError:
        return templates.TemplateResponse("index.html", {"request": request, "outputLab1": "Помилка: n має бути цілим числом. Спробуйте ще раз."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    