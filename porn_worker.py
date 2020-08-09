import requests

class PornWorker:
    def __init__ (self):
        self.categories = None
    
    def check_if_valid_url (self, message):
        try:
            requests.get("http://www.avalidurl.com/")
            print("URL is valid and exists on the internet")
        except requests.ConnectionError:
            print("URL does not exist on Internet")

    def load_categories (self):
        with open("./metainfo/categories.txt", 'r') as f:
            self.categories = set(f.readlines())
    
    def check_if_is_category(self, value):
        if not self.categories:
            self.load_categories()
        return value.strip() in self.categories