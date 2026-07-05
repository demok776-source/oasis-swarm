#!/usr/bin/env python3
"""
OASIS Memory Fabric — Document Ingestion Pipeline
Chunks documents → generates embeddings → upserts to Qdrant

Usage:
  pip install qdrant-client openai tiktoken pypdf python-docx
  python3 ingest.py --qdrant http://QDRANT_IP:6333 --collection oasis_docs --path ./docs/
"""
import os, sys, json, uuid, argparse, hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance
    import openai
    import tiktoken
except ImportError:
    print("Install deps: pip install qdrant-client openai tiktoken pypdf python-docx")
    sys.exit(1)

# ── CONFIG ────────────────────────────────────────────────────────
EMBED_MODEL    = "text-embedding-3-small"
EMBED_DIM      = 1536
CHUNK_SIZE     = 512    # tokens
CHUNK_OVERLAP  = 64     # tokens
BATCH_SIZE     = 100    # points per upsert

enc = tiktoken.get_encoding("cl100k_base")

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunks.append(enc.decode(tokens[start:end]))
        start += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 20]

def read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in ['.txt', '.md', '.py', '.cs', '.ts', '.js', '.yaml', '.yml', '.json']:
        return path.read_text(errors='replace')
    if suffix == '.pdf':
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            return '\n'.join(p.extract_text() or '' for p in reader.pages)
        except Exception as e:
            print(f"  PDF error {path.name}: {e}")
            return ''
    if suffix in ['.docx']:
        try:
            import docx
            doc = docx.Document(str(path))
            return '\n'.join(p.text for p in doc.paragraphs)
        except Exception as e:
            print(f"  DOCX error {path.name}: {e}")
            return ''
    return ''

def get_embeddings(client_openai: openai.OpenAI, texts: List[str]) -> List[List[float]]:
    resp = client_openai.embeddings.create(model=EMBED_MODEL, input=texts)
    return [e.embedding for e in resp.data]

def ingest(qdrant_url: str, collection: str, source_path: str, module: str = "oasis"):
    qdrant = QdrantClient(url=qdrant_url)
    oai    = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    
    source = Path(source_path)
    files  = list(source.rglob('*')) if source.is_dir() else [source]
    files  = [f for f in files if f.is_file() and f.suffix in [
        '.txt', '.md', '.py', '.cs', '.ts', '.js',
        '.yaml', '.yml', '.json', '.pdf', '.docx'
    ]]
    
    print(f"Found {len(files)} files in {source_path}")
    
    points_batch: List[PointStruct] = []
    total_chunks  = 0

    for file in files:
        print(f"\n  Processing: {file.name}")
        text = read_file(file)
        if not text.strip():
            print(f"    Empty/unreadable — skip")
            continue

        chunks = chunk_text(text)
        print(f"    {len(chunks)} chunks")

        for i in range(0, len(chunks), 32):
            batch     = chunks[i:i+32]
            embeddings = get_embeddings(oai, batch)

            for j, (chunk, emb) in enumerate(zip(batch, embeddings)):
                chunk_id = str(uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"{file}:{i+j}"
                ))
                points_batch.append(PointStruct(
                    id=chunk_id,
                    vector=emb,
                    payload={
                        "text":      chunk,
                        "source":    str(file),
                        "filename":  file.name,
                        "module":    module,
                        "type":      file.suffix.lstrip('.'),
                        "chunk_idx": i + j,
                        "timestamp": datetime.utcnow().isoformat(),
                        "hash":      hashlib.md5(chunk.encode()).hexdigest(),
                    }
                ))
                total_chunks += 1

            # Upsert in batches
            if len(points_batch) >= BATCH_SIZE:
                qdrant.upsert(collection_name=collection, points=points_batch)
                print(f"    Upserted {len(points_batch)} points")
                points_batch = []

    # Final batch
    if points_batch:
        qdrant.upsert(collection_name=collection, points=points_batch)
        print(f"    Final upsert: {len(points_batch)} points")

    # Summary
    info = qdrant.get_collection(collection)
    print(f"\n{'═'*50}")
    print(f"Collection: {collection}")
    print(f"Total chunks ingested: {total_chunks}")
    print(f"Total vectors in collection: {info.points_count}")
    print(f"{'═'*50}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OASIS Memory Fabric Ingestor")
    parser.add_argument("--qdrant",     required=True, help="Qdrant URL, e.g. http://IP:6333")
    parser.add_argument("--collection", required=True, help="Collection name")
    parser.add_argument("--path",       required=True, help="File or directory to ingest")
    parser.add_argument("--module",     default="oasis", help="Module tag for payload")
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        # Try Anthropic embeddings as fallback stub
        print("Warning: OPENAI_API_KEY not set. Set it for embeddings.")
        sys.exit(1)

    ingest(args.qdrant, args.collection, args.path, args.module)
