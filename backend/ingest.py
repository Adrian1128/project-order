import os
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from langchain_docling.loader import DoclingLoader

# Define the path to your raw SSSL documents
DATA_DIR = "./data"

# Configure Docling to skip OCR (reasding only the digital text layer)
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False

# Create a custom converter that applies the No OCR rule to PDFs
custom_converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

def load_documents_from_directory(directory_path: str):
    """
    Scans a directory and uses Docling's advanced AI layout parser
    to extract text from PDFs, Word docs, and text files.
    """
    all_documents = []

    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return all_documents

    print(f"Scanning directory: {directory_path}...\n")

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # Skip directories
        if os.path.isdir(file_path):
            continue

        print(f"🧠 Parsing layout for: {filename}")

        try:
            # Pass the custom_converter into the LangChain loader
            loader = DoclingLoader(file_path=file_path, converter=custom_converter)
            docs = loader.load()
            all_documents.extend(docs)
            print(f"   ✅ Success! Loaded {len(docs)} segments.")

        except Exception as e:
            print(f"   ❌ Failed to load {filename}. Error: {e}")

    print(
        f"\n✅ Pipeline Complete: Extracted {len(all_documents)} total document chunks."
    )
    return all_documents


# --- Test the pipeline ---
if __name__ == "__main__":
    documents = load_documents_from_directory(DATA_DIR)

    if documents:
        print("\n--- Content Preview ---")
        print(documents[1].page_content[:400] + "...\n")
        print(f"Metadata: {documents[0].metadata}")
