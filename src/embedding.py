from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def embed_text(self, text):
        return self.model.encode(text)
    
    def embed_chunks(self, chunks):
        for chunk in chunks:
            embedding = self.model.encode(chunk["text"])
            chunk["embedding"] = embedding.tolist()
        return chunks
    
    def get_dimension(self):
        sample_embedding = self.model.encode("test")
        return len(sample_embedding)
