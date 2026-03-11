import faiss
import numpy as np

class VectorStore:
    def __init__(self, dimension):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks = []
    
    def add_chunks(self, chunks):
        embeddings = np.array([c["embedding"] for c in chunks]).astype("float32")
        self.index.add(embeddings)
        self.chunks.extend(chunks)
    
    def search(self, query_vector, k=5):
        query_vector = np.array([query_vector]).astype("float32")
        distances, indices = self.index.search(query_vector, k=k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                results.append({
                    "chunk": self.chunks[idx],
                    "distance": float(distances[0][i])
                })
        return results
    
    def save(self, filepath):
        faiss.write_index(self.index, filepath)
    
    def load(self, filepath):
        self.index = faiss.read_index(filepath)
