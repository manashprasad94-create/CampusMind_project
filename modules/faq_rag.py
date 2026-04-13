# modules/faq_rag.py

import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

load_dotenv()

# Global variables
_faq_chain = None

def _load_faq_chain():
    """Load chain only when first needed"""
    global _faq_chain

    if _faq_chain is not None:
        return _faq_chain

    print("🧠 Loading FAQ RAG pipeline...")

    if not os.path.exists("vectorstore/faq_index"):
        raise FileNotFoundError(
            "FAQ index not found! Please run ingest.py first."
        )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        "vectorstore/faq_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )

    prompt_template = """
You are EduAssist, a helpful and friendly college FAQ assistant.
Answer the student's question based on the context provided.
Always respond in the same language the student asks in.
If the answer is not in the context, say:
"I don't have that information in my FAQ yet.
Please contact the admissions office directly."

Context:
{context}

Student Question: {question}

Answer:
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    _faq_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": 3}
        ),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False
    )

    print("✅ FAQ RAG pipeline ready!")
    return _faq_chain


def get_faq_answer(question: str) -> str:
    try:
        chain = _load_faq_chain()
        response = chain.invoke({"query": question})
        return response["result"]
    except FileNotFoundError as e:
        return str(e)
    except Exception as e:
        return f"Error: {str(e)}"