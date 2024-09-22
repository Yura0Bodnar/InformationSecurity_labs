from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import configparser

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

        sequence = linear_congruential_generator(m, a, c, x0, inputLab1)
        result = " ".join(map(str, sequence))
        return templates.TemplateResponse("index.html", {"request": request, "outputLab1": result})

    except ValueError:
        return templates.TemplateResponse("index.html", {"request": request, "outputLab1": "Помилка: n має бути цілим числом. Спробуйте ще раз."})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    