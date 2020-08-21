import pandas as pd
from security.token import UserToken
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

class ML_Worker:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def loaddata(self):
        chat_secure_id = UserToken(self.chat_id).get_token()
        self.projects = pd.read_csv("./metainfo/daily-best.csv") # here gotta be best of today's porn (or best by each popular category)
        self.projects_done = pd.read_csv('./user-data/{}/ml-data/ratings.csv'.format(chat_secure_id))
        self.projects.head()

    def clean_data(self):
        self.projects = self.projects.drop_duplicates(subset="link", keep='first', inplace=False)
        fieldnames = ['title', 'link', 'tags', 'description', 'timestamp', 'rating']
        for field in fieldnames:
            self.projects[field] = self.projects[field].fillna('')

    def combine(self):
        self.projects["text"] = self.projects["title"] + ' ' + self.projects["tags"] + ' ' + self.projects["description"]

    def calculate_tf_idf(self):
        tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
        tfidf_matrix = tf.fit_transform(self.projects['text'])
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
