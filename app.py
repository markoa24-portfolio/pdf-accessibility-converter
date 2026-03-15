import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
import io

st.title("PDF to Accessible HTML Remediation Tool")

st.write(
    "Upload a PDF document to automatically convert it into clean, structured, accessibility-compliant HTML."
)

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:

    st.write("Extracting text...")

    # Read PDF bytes ONCE
    pdf_bytes = uploaded_file.read()

    # Use BytesIO so PyPDF2 can read it properly
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

    extracted_text = ""

    # Try normal text extraction first
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"

    # If no selectable text found → run OCR
    if not extracted_text.strip():
        st.write("No selectable text found. Running OCR...")

        images = convert_from_bytes(pdf_bytes)
        st.write(f"Number of images created: {len(images)}")

        for i, img in enumerate(images):
            st.write(f"Running OCR on page {i+1}...")
            ocr_text = pytesseract.image_to_string(img)
            st.write(f"OCR text length (page {i+1}): {len(ocr_text)}")
            extracted_text += ocr_text + "\n"

    # Show debugging information
    st.write(f"Total extracted text length: {len(extracted_text)}")
    st.write("Preview of extracted text:")
    st.text(extracted_text[:500])

    # If still empty → stop
    if not extracted_text.strip():
        st.error("OCR did not extract any readable text.")
        st.stop()

    st.write("Sending to Gemini...")

    # Initialize Gemini client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    st.subheader("Generated HTML Output")
    st.code(response.text, language="html")
