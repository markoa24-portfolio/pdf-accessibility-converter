import streamlit as st
from google import genai
import os
import PyPDF2

st.title("PDF to Accessible HTML Remediation Tool")

st.write(
    "Upload a PDF document to automatically convert it into clean, structured, accessibility-compliant HTML."
)

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:

    st.write("Extracting text...")

    # Extract text from PDF
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    extracted_text = ""

    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"

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