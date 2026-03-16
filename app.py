import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
import io

# Configure Gemini (secure — uses Render environment variable)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.title("PDF to Accessible HTML Remediation Tool")

st.write(
    "Upload a PDF document to automatically convert it into clean, structured, accessibility-compliant HTML."
)

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:

    st.write("Extracting text...")

    pdf_bytes = uploaded_file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

    extracted_text = ""

    # First try normal text extraction
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"

    # If no selectable text found → use OCR
    if not extracted_text.strip():
        st.write("No selectable text found. Running OCR...")

        num_pages = len(pdf_reader.pages)

        for page_number in range(num_pages):
            st.write(f"Running OCR on page {page_number + 1}...")

            images = convert_from_bytes(
                pdf_bytes,
                first_page=page_number + 1,
                last_page=page_number + 1,
                dpi=150  # Lower DPI for better speed on free tier
            )

            img = images[0]
            ocr_text = pytesseract.image_to_string(img)
            extracted_text += ocr_text + "\n"

    if not extracted_text.strip():
        st.error("OCR did not extract any readable text.")
        st.stop()

    st.write("Sending to Gemini...")

    prompt = f"""
You are an accessibility remediation expert.

Convert the following PDF content into clean, semantic, WCAG-compliant HTML.

Requirements:
- Use proper semantic tags (h1, h2, h3, p, ul, ol, li, table, thead, tbody, th, td).
- Preserve document structure.
- Do NOT add styling.
- Ensure logical heading hierarchy.
- Output only clean HTML.

Content:
{extracted_text}
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    st.subheader("Generated HTML Output")
    st.code(response.text, language="html")
