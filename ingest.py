# ingest.py

import os
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

def ingest_faq(pdf_path: str = "data/FAQ-JIS.pdf"):

    print("📄 Loading FAQ PDF with Docling...")
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    markdown_text = result.document.export_to_markdown()
    print("✅ PDF converted to markdown")

    # Wrap in LangChain Document
    docs = [Document(page_content=markdown_text)]

    print("✂️ Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["Q.", "\n\n", "\n", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ Created {len(chunks)} chunks")

    print("🧠 Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print("✅ Embedding model loaded")

    print("💾 Creating FAISS vectorstore...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("vectorstore/faq_index")
    print("✅ Vectorstore saved to vectorstore/faq_index")

    return vectorstore

if __name__ == "__main__":
    ingest_faq()