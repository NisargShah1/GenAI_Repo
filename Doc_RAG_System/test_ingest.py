from src.ingest import process_single_document, get_embedding_function

def test_progress(progress, message):
    print(f"Progress: {progress*100:.2f}% - {message}")

embedding_fn = get_embedding_function("huggingface")
process_single_document("data/gpt4.pdf", embedding_fn, test_progress)
