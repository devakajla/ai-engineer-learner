from datetime import date

from fastapi import FastAPI
from pydantic import BaseModel, Field, computed_field, model_validator

app = FastAPI()
