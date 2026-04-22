from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import API_DIR

OLLAMA_MODEL = "gemma3:4b"
OLLAMA_EMBED_MODEL = "nomic-embed-text:latest"
RAG_PDF_PATH = API_DIR / "rag" / "Hand Gesture Description.pdf"

_vector_store: FAISS | None = None
_llm: OllamaLLM | None = None


async def init_rag() -> None:
    global _vector_store, _llm

    if not RAG_PDF_PATH.exists():
        print(f"WARNING: RAG PDF missing at {RAG_PDF_PATH}. AI Tutor disabled.")
        return

    print(f"INFO:     Loading RAG Corpus from: {RAG_PDF_PATH.name}")

    try:
        loader = PyPDFLoader(str(RAG_PDF_PATH))
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = text_splitter.split_documents(documents)
        print(f"INFO:     Embedding {len(chunks)} chunks via Ollama ({OLLAMA_MODEL})...")

        embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)
        _vector_store = FAISS.from_documents(chunks, embeddings)

        _llm = OllamaLLM(model=OLLAMA_MODEL)
        print("INFO:     RAG pipeline ready.")
    except Exception as e:
        print(f"ERROR:    RAG init failed — ensure Ollama is running with '{OLLAMA_MODEL}'. Detail: {e}")


async def get_feedback(expected_sign: str, predicted_sign: str) -> str:
    if _vector_store is None or _llm is None:
        return "The AI Tutor is still warming up. Please try again in a moment!"

    try:
        # Search specifically for each sign to maximise relevance
        docs_expected = _vector_store.similarity_search(
            f"How to sign the letter '{expected_sign}' hand shape fingers position", k=3
        )
        docs_predicted = _vector_store.similarity_search(
            f"How to sign the letter '{predicted_sign}' hand shape fingers position", k=2
        )

        # Deduplicate by page content
        seen = set()
        unique_docs = []
        for doc in docs_expected + docs_predicted:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_docs.append(doc)

        context = "\n\n---\n\n".join([doc.page_content for doc in unique_docs])

        prompt_template = PromptTemplate(
            template=(
                "You are a Sinhala Sign Language tutor helping a student.\n\n"
                "TASK: The student was trying to sign the letter '{expected}' but the camera "
                "recognised their gesture as '{predicted}' instead.\n\n"
                "RULES:\n"
                "- ONLY use information from the textbook context below.\n"
                "- ONLY discuss the letters '{expected}' and '{predicted}' — do NOT mention any other letters.\n"
                "- Describe the exact hand/finger difference between '{predicted}' and '{expected}'.\n"
                "- Keep your answer to exactly 2-3 sentences. Be encouraging but precise.\n"
                "- Focus on actionable physical corrections (finger positions, palm orientation, etc).\n\n"
                "TEXTBOOK CONTEXT:\n{context}\n\n"
                "Your correction for the student:"
            ),
            input_variables=["expected", "predicted", "context"],
        )

        prompt = prompt_template.format(
            expected=expected_sign,
            predicted=predicted_sign,
            context=context,
        )
        response = _llm.invoke(prompt)
        return response.strip()

    except Exception as e:
        print(f"RAG inference error: {e}")
        return "I had trouble generating feedback. Check your Ollama service and try again!"
