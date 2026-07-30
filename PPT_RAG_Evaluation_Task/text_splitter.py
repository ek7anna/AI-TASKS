from langchain_text_splitters import RecursiveCharacterTextSplitter
from ppt_loader import load_ppt, find_ppt_path

def get_slide_chunks(ppt_path=None):
    if ppt_path is None:
        ppt_path = find_ppt_path()
        
    slides = load_ppt(ppt_path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    all_chunks = []
    for slide in slides:
        if not slide["text"]:
            continue
        chunks = splitter.split_text(slide["text"])
        for i, chunk in enumerate(chunks, start=1):
            all_chunks.append({
                "slide": slide["slide"],
                "chunk": i,
                "text": chunk
            })
    return all_chunks

if __name__ == "__main__":
    try:
        chunks = get_slide_chunks()
        print(f"\nTotal Chunks Created: {len(chunks)}\n")
        for chunk in chunks[:10]: # Print first 10 chunks as sample
            print("=" * 50)
            print(f"Slide : {chunk['slide']}")
            print(f"Chunk : {chunk['chunk']}")
            print(chunk["text"].encode('ascii', errors='replace').decode('ascii'))
    except Exception as e:
        print(f"Error splitting text: {e}")
