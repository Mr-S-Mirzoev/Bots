import requests

databases = ['www.its.porn', 'www.xnxx.com']

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
            self.categories = set(x.strip() for x in f.readlines())
    
    def check_if_is_category(self, value):
        if not self.categories:
            self.load_categories()
        return value.strip() in self.categories

    def check_if_has_categories(self, text: str):
        lst = [x.lower() for x in text.split()]
        cats = list()
        length = len(lst)
        for i in range(length):
            if self.check_if_is_category(lst[i]):
                cats.append(lst[i])
        for wordcount in range(2, 4 + 1):
            for i in range(length - wordcount + 1):
                val = ' '.join(lst[i : i + wordcount])
                if self.check_if_is_category(val):
                    cats.append(val)
        return cats