import re
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

        if re.search(pattern, lower_text):
            found.append({
                "Ingredient": info["name"],
                "Risk": info["risk"]
            })

    return found

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🧪 Food Ingredient Scanner")
st.write("Upload or take a photo of food ingredients and detect potentially harmful additives.")

st.subheader("📤 Upload Image")
uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png"]
)

st.subheader("📸 Camera Capture")
camera_image = st.camera_input("Take a picture")

image = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)

elif camera_image is not None:
    image = Image.open(camera_image)

if image is not None:
    st.image(image, caption="Selected Image", use_container_width=True)

    with st.spinner("Reading text with OCR..."):
        extracted_text = extract_text(image)

    st.subheader("📝 Extracted Text")
    st.text_area("OCR Result", extracted_text, height=200)

    harmful_found = find_harmful_ingredients(extracted_text)

    st.subheader("⚠️ Detected Harmful Ingredients")

    if harmful_found:
        df = pd.DataFrame(harmful_found)
        st.dataframe(df, use_container_width=True)

        for item in harmful_found:
            st.warning(f"{item['Ingredient']} → {item['Risk']}")

    else:
        st.success("No harmful ingredients detected.")

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("---")
st.caption("Supports Bulgarian and English OCR using EasyOCR")
