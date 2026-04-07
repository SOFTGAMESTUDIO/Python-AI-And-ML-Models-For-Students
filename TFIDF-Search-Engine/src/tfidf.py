from sklearn.feature_extraction.text import TfidfVectorizer

def train(docs):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )
    matrix = vectorizer.fit_transform(docs)
    return vectorizer, matrix