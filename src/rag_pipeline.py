from .embedding import EmbeddingModel
from .vector_store import VectorStore
from config import EMBEDDING_MODEL

class RAGPipeline:
    def __init__(self, model_name=EMBEDDING_MODEL):
        self.embedding_model = EmbeddingModel(model_name)
        self.vector_store = None
    
    def build_index(self, chunks):
        chunks_with_embeddings = self.embedding_model.embed_chunks(chunks)
        
        dimension = self.embedding_model.get_dimension()
        self.vector_store = VectorStore(dimension)
        self.vector_store.add_chunks(chunks_with_embeddings)
        
        return chunks_with_embeddings
    
    def query(self, query_text, k=5):
        if not self.vector_store:
            raise ValueError("Index not built. Call build_index first.")
        
        query_vector = self.embedding_model.embed_text(query_text)
        return self.vector_store.search(query_vector, k=k)
    
    def save_index(self, filepath):
        if self.vector_store:
            self.vector_store.save(filepath)
    
    def load_index(self, filepath, chunks):
        dimension = self.embedding_model.get_dimension()
        self.vector_store = VectorStore(dimension)
        self.vector_store.load(filepath)
        self.vector_store.chunks = chunks
