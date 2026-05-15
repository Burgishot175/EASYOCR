import re
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import easyocr

st.set_page_config(
    page_title="Food Ingredient Scanner",
    page_icon="🧪",
    layout="centered"
)

# -------------------------------------------------
# OCR Reader
# -------------------------------------------------
@st.cache_resource

def load_reader():
    return easyocr.Reader(['bg', 'en'], gpu=False)

reader = load_reader()

# -------------------------------------------------
# Harmful ingredients database
# -------------------------------------------------
harmful_ingredients = {
    "e621": {
        "name": "E621 (Monosodium Glutamate)",
        "risk": "Flavor enhancer that may cause headaches or sensitivity in some people."
    },
    "msg": {
        "name": "MSG",
        "risk": "Artificial flavor enhancer."
    },
    "palm oil": {
        "name": "Palm Oil",
        "risk": "Highly processed fat linked to environmental and health concerns."
    },
    "палмово масло": {
        "name": "Палмово масло",
        "risk": "Силно преработена мазнина с потенциални здравословни рискове."
    },
    "e250": {
        "name": "E250 (Sodium Nitrite)",
        "risk": "Preservative associated with processed meats."
    },
    "e951": {
        "name": "E951 (Aspartame)",
        "risk": "Artificial sweetener that may not be suitable for everyone."
    },
    "high fructose corn syrup": {
        "name": "High Fructose Corn Syrup",
        "risk": "Highly processed sweetener."
    },
    "hydrogenated": {
        "name": "Hydrogenated Oils",
        "risk": "May contain trans fats."
    },
    "trans fat": {
        "name": "Trans Fat",
        "risk": "Associated with cardiovascular disease."
    },
    "e102": {
        "name": "E102 (Tartrazine)",
        "risk": "Artificial coloring that may cause hyperactivity in some children."
    },
}

# -------------------------------------------------
# Functions
# -------------------------------------------------
def extract_text(image):
    image_np = np.array(image)
    results = reader.readtext(image_np, detail=0)
    text = " ".join(results)
    return text


def find_harmful_ingredients(text):
    found = []
    lower_text = text.lower()

    for ingredient, info in harmful_ingredients.items():
        pattern = re.escape(ingredient.lower())

st.caption("Supports Bulgarian and English OCR using EasyOCR")
