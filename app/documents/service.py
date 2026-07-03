


from app.documents.enums import DocumentType
from app.documents.models import Document
from app.documents.repo import DocumentRepo


class DocumentService: 
    def __init__(self, repo: DocumentRepo): 
        self.repo = repo 

    def create(self, type: str, title: str) -> Document:
        return self.repo.create(type, title)

    def get_document_id(self, document_id: int) -> Document | None: 
        return self.repo.get(document_id)

    def list_all(self) -> list[Document]: 
        return self.repo.list_all()
    
    def update(self, document_id: int, title: str) -> Document | None: 
        return self.repo.update(document_id, title)
    


