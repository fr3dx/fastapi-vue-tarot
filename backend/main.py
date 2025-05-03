from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict
import os
import random
import json

app = FastAPI()

# CORS beállítás
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mappaútvonalak
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_DIR: str = os.path.join(BASE_DIR, "cards-test")
app.mount("/cards", StaticFiles(directory=CARDS_DIR), name="cards")

# Leírások betöltése
with open(os.path.join(BASE_DIR, "card_description.json"), "r", encoding="utf-8") as f:
    CARD_DESCRIPTIONS: Dict[str, str] = json.load(f)

# 📦 Pydantic modellek
class Card(BaseModel):
    name: str
    image_url: str
    key: str

class CardDescription(BaseModel):
    description: str

# 🧠 Formázófüggvény
def format_card_name(filename: str) -> str:
    name_part = os.path.splitext(filename)[0]
    name = name_part.split("_", 1)[-1]
    return "The " + name.replace("-", " ").replace("_", " ").title()

# ✅ Véletlen kártya húzása
@app.get("/api/daily_card", response_model=Card)
async def get_daily_card() -> Card:
    png_files: list[str] = [f for f in os.listdir(CARDS_DIR) if f.lower().endswith(".png")]
    selected: str = random.choice(png_files)
    card_name: str = format_card_name(selected)
    key: str = selected.split("_", 1)[-1].split(".")[0].lower()

    return Card(
        name=card_name,
        image_url=f"/cards/{selected}",
        key=key
    )

# ✅ Leírás külön lekérése
@app.get("/api/card_description/{key}", response_model=CardDescription)
async def get_card_description(key: str) -> CardDescription:
    description = CARD_DESCRIPTIONS.get(key)
    if not description:
        description = "Nincs elérhető leírás ehhez a kártyához."
    return CardDescription(description=description)
