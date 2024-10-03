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