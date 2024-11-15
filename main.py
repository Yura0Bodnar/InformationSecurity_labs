from fastapi import FastAPI
from routers import lab1, lab2, lab3, lab4, lab5
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(lab1.router)
app.include_router(lab2.router)
app.include_router(lab3.router)
app.include_router(lab4.router)
app.include_router(lab5.router)
