from app.documents.models import Document

from sqlalchemy.orm import Session
from sqlalchemy import select



class DocumentRepo: 
    def __init__(self, db_session: Session):
        self.db_session = db_session

        def create(self, title: str) -> Document:
            document = Document(title=title)
            self.db_session.add(document)
            self.db_session.commit()
            self.db_session.refresh(document)
            return document
        
        def update(self, document_id: int, title: str) -> Document | None: 
            statement = select(Document).where(Document.id == document_id)
            document = self.db_session.execute(statement).scalar_one_or_none()

            if document is None: 
                return None
            
            if title is not None: 
                document.title = title
            
            self.db_session.commit()
            self.db_session.refresh(document)
            return document
        
        def delete(self, document_id: int) -> bool: 
            document = self.db_session.query(document).filter(Document.id == document_id).one_or_none()

            if document is None: 
                return False

            self.db_session.delete(document)
            self.db_session.commit()
            return True

        def get_document_id(self, document_id: int) -> Document | None: 
            return self.db_session.query(Document).filter(Document.id == document_id).one_or_none()
        
        def list_all(self) -> list[Document]:
            return self.db_session.query(Document).all()
        
        