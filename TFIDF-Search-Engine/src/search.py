from sklearn.metrics.pairwise import cosine_similarity

def query(q, vectorizer, matrix, docs, top_k=3):
    q_vec = vectorizer.transform([q])
    scores = cosine_similarity(q_vec, matrix)[0]

    idxs = scores.argsort()[-top_k:][::-1]

    results = []
    for i in idxs:
        if scores[i] > 0.15:
            results.append((docs[i], scores[i]))

    return results