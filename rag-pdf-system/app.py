import os
import sys
import tempfile
from pathlib import Path

root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

import streamlit as st
from main import run_pipeline

st.set_page_config(page_title="RAG PDF System", layout="wide")

st.title("RAG PDF System")

st.sidebar.header("Upload PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

question = st.text_input("Ask a question about the PDF")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.sidebar.success("PDF uploaded successfully")

    if question:
        with st.spinner("Processing..."):
            answer, sources = run_pipeline(tmp_path, question)

        st.subheader("Answer")
        st.write(answer)

        if sources:
            st.subheader("Top Retrieved Chunks")
            for idx, source in enumerate(sources, 1):
                page = source.get("page")
                score = source.get("score")
                page_label = f"page {page}" if page else "unknown page"
                st.markdown(f"**Chunk {idx} ({page_label}, score {score:.3f}):** {source['text']}")
else:
    st.info("Upload a PDF file to begin.")
