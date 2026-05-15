import streamlit as st
import easyocr
import numpy as np
from PIL import Image

# Конфигурация на страницата
st.set_page_config(page_title="Скенер за вредни съставки", page_icon="🔍")

# Инициализиране на OCR четеца (кешираме го, за да не се зарежда при всяко кликване)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['bg', 'en'])

reader = load_reader()

# Списък с вредни съставки (може да се разширява)
HARMFUL_INGREDIENTS = {
    "E621": "Мононатриев глутамат (Monosodium Glutamate) - усилвател на вкуса.",
    "ПАЛМОВО МАСЛО": "Палмово масло (Palm Oil) - високо съдържание на наситени мазнини.",
    "PALM OIL": "Палмово масло (Palm Oil) - високо съдържание на наситени мазнини.",
    "E250": "Натриев нитрит - консервант в колбасите.",
    "АСПАРТАМ": "Изкуствен подсладител (Aspartame).",
    "ASPARTAME": "Изкуствен подсладител (Aspartame).",
    "ФРУКТОЗЕН СИРОП": "Високофруктозен сироп от царевица (HFCS).",
    "FRUCTOSE SYRUP": "Високофруктозен сироп от царевица (HFCS)."
}

def process_image(image):
    # Конвертиране на изображението за EasyOCR
    img_array = np.array(image)
    with st.spinner('Анализиране на текста...'):
        results = reader.readtext(img_array, detail=0)
    return results

def check_ingredients(text_list):
    found = []
    full_text = " ".join(text_list).upper()
    
    for ingredient, description in HARMFUL_INGREDIENTS.items():
        if ingredient in full_text:
            found.append(description)
    return found

# --- ИНТЕРФЕЙС ---
st.title("🔍 Скенер за вредни съставки")
st.write("Качете снимка на етикета със съдържанието, за да проверите за опасни добавки.")

tab1, tab2 = st.tabs(["📁 Качване на файл", "📸 Камера"])

uploaded_file = None

with tab1:
    file_upload = st.file_uploader("Изберете снимка...", type=["jpg", "jpeg", "png"])
    if file_upload:
        uploaded_file = file_upload

with tab2:
    camera_photo = st.camera_input("Направете снимка на етикета")
    if camera_photo:
        uploaded_file = camera_photo

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Вашата снимка', use_column_width=True)
    
    if st.button("Провери съставките"):
        extracted_text = process_image(image)
        
        st.subheader("Разпознат текст:")
        st.write(", ".join(extracted_text))
        
        st.divider()
        
        harmful_found = check_ingredients(extracted_text)
        
        if harmful_found:
            st.error("⚠️ Внимание! Намерени са потенциално вредни съставки:")
            for item in harmful_found:
                st.write(f"- {item}")
        else:
            st.success("✅ Не бяха открити съставки от черния списък.")
