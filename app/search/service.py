from app.search.repo import SearchRepo


class SearchService: 
    def __init__(self, repo:SearchRepo): 
        self.repo = repo

        