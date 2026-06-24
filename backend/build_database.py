from langchain_text_splitters import RecursiveCharacterTextSplitter

from ingest import load_documents_from_directory
from db_manager import DatabaseManager
from config import DATA_DIR


def run_pipeline():
    # 1. Initialize our modular manager
    db = DatabaseManager()

    # 2. Extract texts using Docling
    raw_documents = load_documents_from_directory(DATA_DIR)
    if not raw_documents:
        print("Pipeline aborted: No data extracted.")
        return

    # 3. Handle paragraph segmentation
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    chunked_documents = text_splitter.split_documents(raw_documents)

    # 4. Wipe old records and construct fresh vectors
    db.initialize_collection()
    db.insert_documents(chunked_documents)


if __name__ == "__main__":
    run_pipeline()
