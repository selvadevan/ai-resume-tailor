# app.py

import streamlit as st
import os
from io import BytesIO

# Import your core modules here
# Adjust as per your repo/module structure
from groq_resume_extractor import GroqResumeExtractor
from document_converter_groq import DocumentConverter
from job_description_parser import JobDescriptionParser
from resume_generator import ResumeGenerator

st.set_page_config(page_title="AI Resume Tailoring System", layout="wide")

st.title("AI Resume Tailoring System")

st.sidebar.header("Configuration")

groq_api_key = st.sidebar.text_input("Enter your Groq API Key", type="password")
model_name = st.sidebar.text_input("Model Name", value="mixtral-8x7b-32768")

if not groq_api_key:
    st.warning("Please enter your Groq API Key in the sidebar.")
    st.stop()

# File uploaders
st.header("1. Upload Files")

col1, col2 = st.columns(2)
with col1:
    uploaded_resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf","docx"])
with col2:
    uploaded_jd = st.file_uploader("Upload Job Description (TXT or DOCX)", type=["txt","docx"])

output_format = st.selectbox("Select output format", ["DOCX", "PDF"])

if st.button("Tailor Resume"):
    if not uploaded_resume or not uploaded_jd:
        st.error("Please upload both a resume and a job description.")
        st.stop()

    with st.spinner("Processing..."):
        # 1. Convert files to text
        resume_converter = DocumentConverter(uploaded_resume)
        resume_text = resume_converter.to_text()

        jd_converter = DocumentConverter(uploaded_jd)
        jd_text = jd_converter.to_text()

        # 2. Extract resume data
        extractor = GroqResumeExtractor(api_key=groq_api_key, model=model_name)
        resume_data = extractor.extract(resume_text)

        # 3. Parse job description
        parser = JobDescriptionParser()
        parsed_jd = parser.parse(jd_text)

        # 4. Tailor resume
        generator = ResumeGenerator(api_key=groq_api_key, model=model_name)
        tailored_resume = generator.generate(resume_data, parsed_jd)

        # 5. Offer download
        output_buffer = BytesIO()
        if output_format == "DOCX":
            generator.to_docx(tailored_resume, output_buffer)
            output_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            output_ext = "docx"
        else:
            generator.to_pdf(tailored_resume, output_buffer)
            output_mime = "application/pdf"
            output_ext = "pdf"

        st.success("Resume tailored successfully!")
        st.download_button(
            label="Download Tailored Resume",
            data=output_buffer.getvalue(),
            file_name=f"tailored_resume.{output_ext}",
            mime=output_mime
        )
