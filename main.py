import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pipeline import process_document
from fetchers import fetch_file

# Configure logging once
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_any_document(source: str, keep_temp=False):
    """
    Fetch (local or remote) and process a document, returning structured results.
    """
    local_path, cleanup = fetch_file(source, keep=keep_temp)
    try:
        result = process_document(str(local_path), source, skip_if_duplicate=False)
        status = result.status
        doc_id = result.doc_id
        logger.info(f"Processed '{source}' with status '{status}' (doc_id={doc_id})")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to process {source}: {e}")
        return {"source": source, "status": "exception", "error": str(e)}
    finally:
        cleanup()

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

def print_summary(results):

    success = sum(1 for r in results if r.status == "success")
    skipped = sum(1 for r in results if r.status == "skipped_duplicate")
    failed = sum(1 for r in results if r.status not in ("success", "skipped_duplicate"))

    logger.info("Processing summary:")
    logger.info(f"  ✅ Success: {success}")
    logger.info(f"  ⏭️  Skipped duplicates: {skipped}")
    logger.info(f"  ❌ Failed: {failed}")
    logger.info(f"  Total processed: {len(results)}")

if __name__ == "__main__":
    
    local_files = collect_local_files("/home/nikola/rag_temp", recursive=True)

    urls = [
        "https://www.index.hr/",
        "https://www.index.hr/vijesti/clanak/kod-sibenika-zena-kilometrima-vozila-na-felgama-policija-ju-uhitila/2716865.aspx?index_ref=naslovnica_vijesti_ostalo_d_0"
    ]

    sources = local_files + urls

    # --- Parallel execution ---
    max_workers = min(8, len(sources))  # 8 threads or fewer if fewer docs
    logger.info(f"Processing {len(sources)} documents in parallel using {max_workers} threads")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_source = {executor.submit(process_any_document, src): src for src in sources}

        for future in as_completed(future_to_source):
            src = future_to_source[future]
            try:
                result = future.result()
                results.append(result)
                logger.info(f"✅ Completed: {src}")
            except Exception as e:
                logger.error(f"❌ Error processing {src}: {e}")

    print_summary(results)