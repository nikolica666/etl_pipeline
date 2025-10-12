from db_store import VectorDBStore
from pipeline import process_document, get_embedding_dimension
from fetchers import fetch_file
from concurrent.futures import ThreadPoolExecutor, as_completed
from extractors.html_extractor import collect_urls
from vectorstore.config import setup_qdrant
import os, logging, requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

embedding_size = get_embedding_dimension()

def _should_include_file(path, extensions):
    """
    Helper to check if file should be included based on extension filter.
    """
    if not extensions:
        return True
    _, ext = os.path.splitext(path)
    return ext.lower() in [e.lower() for e in extensions]

def collect_local_files(folder_path, recursive=False, extensions=None):
    """
    Collect all files from a folder, optionally searching recursively.

    Args:
        folder_path (str): The directory to search.
        recursive (bool): Whether to search subdirectories recursively.
        extensions (list[str], optional): If provided, only include files
            with these extensions (case-insensitive, e.g. [".txt", ".pdf"]).

    Returns:
        list[str]: List of full file paths.
    """
    if not os.path.isdir(folder_path):
        logger.warning(f"Path '{folder_path}' is not a directory.")
        return []

    collected = []

    if recursive:
        for root, _, files in os.walk(folder_path):
            for filename in files:
                path = os.path.join(root, filename)
                if _should_include_file(path, extensions):
                    collected.append(path)
    else:
        for filename in os.listdir(folder_path):
            path = os.path.join(folder_path, filename)
            if os.path.isfile(path) and _should_include_file(path, extensions):
                collected.append(path)

    logger.info(f"Collected {len(collected)} files from '{folder_path}' (recursive={recursive})")
    return collected

def collect_urls_from(base_url, domain=None, user_agent="MyCrawler/1.0"):
    """Fetch a URL and extract all links from it."""
    headers = {"User-Agent": user_agent}
    response = requests.get(base_url, headers=headers, timeout=10)
    response.raise_for_status()
    return collect_urls(base_url, response.text, domain_limit=domain)

def process_any_document(source: str, keep_temp: bool = False, store: VectorDBStore | None = None):
    """
    Fetch (local or remote) and process a document, then upload it to VectorDB.
    """
    local_path, cleanup = fetch_file(source, keep=keep_temp)
    try:
        result = process_document(
            str(local_path),
            source=source,
            skip_if_duplicate=False,
            store=store,
        )
        logger.info(f"Processed '{source}' → status='{result.status}', doc_id={result.doc_id}")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to process {source}: {e}")
        return {"source": source, "status": "exception", "error": str(e)}
    finally:
        cleanup()

def calculate_max_workers(len_of_sources):
    """
        Count CPU threads (or fallback to 4)

        max_workers = cpu_threads - 2 
        
        If number of source files to process is less then that, 
        fallback to max_workers = len_of_sources
    """
    cpu_threads = os.cpu_count() or 4
    max_workers = min(cpu_threads - 2, len_of_sources)
    logger.info(f"🚀 Calculated parallel processing with {max_workers} workers (CPU has {cpu_threads} threads)")

if __name__ == "__main__":

    # --- DB setup ---
    qdrant, collection = setup_qdrant(embedding_size)
    store = VectorDBStore(qdrant, collection)

    # --- Source setup ---
    local_files = collect_local_files("/home/nikola/rag_temp", recursive=True)
    urls = collect_urls_from("https://www.index.hr/", domain="index.hr") | collect_urls_from("https://www.24sata.hr/", domain="24sata.hr")
    
    sources = urls | set(local_files)
    logger.info(f"📄 Found {len(sources)} sources to process")

    # --- Parallel processing ---
    max_workers = calculate_max_workers(len(sources))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_any_document, src, False, store) for src in sources]
        for future in as_completed(futures):
            try:
                result = future.result()
                logger.info(f"✅ Completed: {result.source if hasattr(result, 'source') else 'Unknown'}")
            except Exception as e:
                logger.error(f"❌ Thread failed: {e}")

    logger.info("🏁 All documents processed.")