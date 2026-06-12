from typing import Protocol
from sqlalchemy.orm import Session
from sqlalchemy import select


class SearchRepoProtocol(Protocol): 

    def create(self, id: int):
        ...

    def get(): 
        ... 
    
    def update():
        ...

    def delete():
        ...

    def list_searches():
        ...  

class SearchRepo: 

    def creat