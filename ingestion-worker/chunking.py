"""Document chunking using LangChain"""
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from config import settings


class DocumentChunker:
    """Chunks documents into overlapping segments"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[dict]:
        """Load PDF and split into chunks"""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        chunks = []
        for doc in documents:
            split_docs = self.splitter.split_documents([doc])
            for i, chunk in enumerate(split_docs):
                chunks.append({
                    "text": chunk.page_content,
                    "metadata": {
                        "source": doc.metadata.get("source", ""),
                        "page": doc.metadata.get("page", 0),
                        "chunk_index": i
                    }
                })
        
        return chunks
    
    def chunk_text(self, text: str, source: str = "") -> List[dict]:
        """Chunk raw text"""
        docs = self.splitter.split_text(text)
        
        chunks = []
        for i, chunk in enumerate(docs):
            chunks.append({
                "text": chunk,
                "metadata": {
                    "source": source,
                    "chunk_index": i
                }
            })
        
        return chunks
