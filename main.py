import os
from pipeline import process_document
from fetchers import fetch_file

def process_any_document(source: str, keep_temp=False):
    """
    Fetch (local or remote) and process a document.
    """
    local_path, cleanup = fetch_file(source, keep=keep_temp)
    try:
        process_document(str(local_path))
    finally:
        cleanup()

if __name__ == "__main__":
    """sample_folder = "/home/nikola/rag_temp/txt"
    count = 0
    for file in os.listdir(sample_folder):
        file_path = os.path.join(sample_folder, file)
        process_any_document(file_path)
        count = count + 1
    print(f"Processed {count} docs")
    """
    process_any_document("https://www.index.hr")
 