import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="🛡️ Скенер за съставки", layout="centered")

# ОБНОВЕНА БАЗА ДАННИ
INGREDIENT_DATABASE = {
    # Оцветители
    "E102": "Тартразин - жълт оцветител, възможен алерген.",
    "E104": "Хинолиново жълто - забранен в някои страни.",
    "E110": "Сънсет жълто - риск от хиперактивност.",
    "E120": "Кармин/Кошенил - извлечен от насекоми, силен алерген.",
    "E122": "Азорубин - синтетичен червен оцветител.",
    "E123": "Амарант - силно ограничена употреба.",
    "E127": "Еритрозин - влияе на щитовидната жлеза.",
    "E131": "Патент синьо V - синтетичен оцветител.",
    "E133": "Брилянтно синьо - изкуствен оцветител.",
    "E151": "Брилянтно черно BN - синтетичен оцветител.",

    # Консерванти
    "E211": "Натриев бензоат - избягвайте с Витамин С.",
    "E250": "Натриев нитрит - потенциален карциноген в колбаси.",
    "E220": "Серен диоксид - консервант, алерген.",
    "E221": "Натриев сулфит.", "E222": "Натриев хидрогенсулфит.",
    "E223": "Натриев метабисулфит.", "E224": "Калиев метабисулфит.",
    "E225": "Калиев сулфит.", "E226": "Калциев сулфит.",
    "E227": "Калциев хидрогенсулфит.", "E228": "Калиев хидрогенсулфит.",

    # Подсладители и овкусители
    "E621": "Мононатриев глутамат - овкусител.",
    "E951": "Аспартам - изкуствен подсладител.",
    "E420": "Сорбитол - подсладител, слабително действие.",

    # Стабилизатори и вредни думи
    "E407A": "Преработени морски водорасли Euchema - стабилизатор.",
    "E412": "Гума гуар - сгъстител, възможен алерген.",
    "МАЛТОДЕКСТРИН": "Малтодекстрин - висок гликемичен индекс.",
    "ПАЛМОВО": "Палмово масло/мазнина - наситени мазнини.",
    "ХИДРОГЕНИРАНИ": "Хидрогенирани мазнини - транс-мазнини.",
    "ЗАХАР": "Внимание: Съдържа захар.",
}

@st.cache_resource
def load_ocr():
    # Изключваме GPU за стабилност в Cloud среди
    return easyocr.Reader(['bg', 'en'], gpu=False)

def normalize_text(text_list):
    raw = " ".join(text_list).upper()
    # Поправка на Е-номера
    t_e = raw.replace("Е", "E").replace("€", "E").replace("I", "1").replace("L", "1")
    t_e = re.sub(r'(?<=E\d)O|O(?=\d)', '0', t_e) # O -> 0
    
    # Поправка за думи (Кирилица)
    caps = {'A': 'А', 'B': 'В', 'E': 'Е', 'K': 'К', 'M': 'М', 'H': 'Н', 'O': 'О', 'P': 'Р', 'C': 'С', 'T': 'Т', 'X': 'Х', 'Y': 'У'}
    t_w = raw
    for lat, cyr in caps.items():
        t_w = t_w.replace(lat, cyr)
    return t_e, t_w

# Интерфейс
st.title("🛡️ Скенер за съставки")

uploaded_file = st.file_uploader("Снимка на етикет", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Важно: Намаляваме размера за пестене на памет!
    img = Image.open(uploaded_file).convert('RGB')
    img.thumbnail((1200, 1200))
    st.image(img)
    
    try:
        reader = load_ocr()
        with st.spinner('Анализиране...'):
            results = reader.readtext(np.array(img), detail=0)
            t_e, t_w = normalize_text(results)
            
            # Търсене
            found = {}
            # Regex за Е-номера
            e_codes = re.findall(r'E\s*(\d+)([A-Z]?)', t_e)
            for m in e_codes:
                code = f"E{m[0]}{m[1]}"
                if code in INGREDIENT_DATABASE: found[code] = INGREDIENT_DATABASE[code]

            # Търсене на думи
            combined = t_w + " " + t_w.replace(" ", "")
            for key, desc in INGREDIENT_DATABASE.items():
                if not key.startswith("E") or len(key) > 4:
                    if key in combined: found[key] = desc

            st.divider()
            if found:
                st.warning("⚠️ Открити съставки:")
                for k, v in found.items(): st.write(f"- **{k}**: {v}")
            else:
                st.success("✅ Няма открити критични съставки.")
    except Exception as e:
        st.error("Възникна грешка при обработката. Опитайте с по-малка снимка.")
