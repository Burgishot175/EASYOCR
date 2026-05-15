import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re

# Настройка на страницата
st.set_page_config(page_title="🛡️ Скенер за съставки", layout="centered")

# ПЪЛНА БАЗА ДАННИ (ВКЛЮЧИТЕЛНО НОВИТЕ Е-НОМЕРА)
INGREDIENT_DATABASE = {
    # Оцветители
    "E102": "Тартразин - жълт оцветител, възможен алерген.",
    "E104": "Хинолиново жълто - забранен в някои страни.",
    "E110": "Сънсет жълто - риск от хиперактивност при деца.",
    "E122": "Азорубин - синтетичен червен оцветител.",
    "E123": "Амарант - силно ограничена употреба.",
    "E127": "Еритрозин - влияе на щитовидната жлеза.",
    "E131": "Патент синьо V - синтетичен оцветител.",
    "E133": "Брилянтно синьо - изкуствен оцветител.",
    "E151": "Брилянтно черно BN - синтетичен оцветител.",
    "E120": "Кармин/Кошенил - оцветител от насекоми, силен алерген.",

    # Консерванти
    "E211": "Натриев бензоат - избягвайте с Витамин С.",
    "E250": "Натриев нитрит - потенциален карциноген.",
    "E220": "Серен диоксид - консервант, алерген.",
    "E221": "Натриев сулфит.", "E222": "Натриев хидрогенсулфит.",
    "E223": "Натриев метабисулфит.", "E224": "Калиев метабисулфит.",
    "E225": "Калиев сулфит.", "E226": "Калциев сулфит.",
    "E227": "Калциев хидрогенсулфит.", "E228": "Калиев хидрогенсулфит.",

    # Подсладители и овкусители
    "E621": "Мононатриев глутамат - овкусител.",
    "E951": "Аспартам - изкуствен подсладител.",
    "E420": "Сорбитол - подсладител, слабително действие.",

    # Вредни думи (Кирилица)
    "МАЛТОДЕКСТРИН": "Малтодекстрин - висок гликемичен индекс.",
    "МАЛТОДЕКАТРИН": "Малтодекстрин (грешка при четене) - висок гликемичен индекс.",
    "ПАЛМОВО": "Палмово масло/мазнина - високо съдържание на наситени мазнини.",
    "ХИДРОГЕНИРАНИ": "Хидрогенирани мазнини - източник на транс-мазнини.",
    "ЗАХАР": "Внимание: Съдържа захар.",
}

# Оптимизирано зареждане: Използваме cache_resource и малък модел
@st.cache_resource
def load_ocr():
    # gpu=False е по-бавно, но по-стабилно срещу сривове при липса на памет
    return easyocr.Reader(['bg', 'en'], gpu=False, model_storage_directory=None)

def normalize_to_cyrillic(text):
    caps = {'A': 'А', 'B': 'В', 'E': 'Е', 'K': 'К', 'M': 'М', 'H': 'Н', 
            'O': 'О', 'P': 'Р', 'C': 'С', 'T': 'Т', 'X': 'Х', 'Y': 'У'}
    for lat, cyr in caps.items():
        text = text.replace(lat, cyr)
    return text

def process_text_and_find_ingredients(text_list):
    raw_text = " ".join(text_list).upper()
    
    # 1. За Е-номера
    text_for_e = raw_text.replace("Е", "E").replace("€", "E").replace("I", "1").replace("O", "0")
    
    # 2. За думи
    text_for_words = normalize_to_cyrillic(raw_text)
    text_no_spaces = text_for_words.replace(" ", "")

    found_results = {}

    # Търсене на Е-номера
    e_pattern = re.compile(r'E\s*(\d+)([A-Z]?)')
    e_matches = e_pattern.findall(text_for_e)
    for match in e_matches:
        code = "E" + match[0] + match[1]
        if code in INGREDIENT_DATABASE:
            found_results[code] = INGREDIENT_DATABASE[code]

    # Търсене на думи
    for key, desc in INGREDIENT_DATABASE.items():
        if not key.startswith("E"):
            if key in text_for_words or key in text_no_spaces:
                found_results[key] = desc

    return found_results, text_for_words

# Интерфейс
st.title("🛡️ Професионален скенер за етикети")

uploaded_file = st.file_uploader("Качете снимка...", type=["jpg", "png"])

if uploaded_file:
    # Намаляваме размера на снимката преди OCR, за да спестим памет
    image = Image.open(uploaded_file).convert('RGB')
    max_size = 1500
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size))
    
    st.image(image, use_container_width=True)
    
    try:
        reader = load_ocr()
        with st.spinner('Анализирам...'):
            img_array = np.array(image)
            results = reader.readtext(img_array, detail=0)
            
            found, debug_text = process_text_and_find_ingredients(results)

            with st.expander("Виж разпознатия текст"):
                st.write(debug_text)

            st.divider()
            if found:
                st.warning("⚠️ Открити съставки:")
                for item, desc in found.items():
                    st.write(f"- **{item}**: {desc}")
            else:
                st.success("✅ Не са открити критични съставки.")
    except Exception as e:
        st.error(f"Грешка при обработката: {e}")
        st.info("Възможно е снимката да е твърде голяма или паметта да е свършила.")
