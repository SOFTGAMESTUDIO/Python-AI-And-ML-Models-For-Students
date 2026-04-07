from src.loader import load_md
from src.tfidf import train
from src.search import query

def main():
    docs = load_md("data/skills.md")
    vectorizer, matrix = train(docs)

    print("\n🤖 AI Knowledge Search (type exit)\n")

    try:
        while True:
            q = input("Ask: ")

            if q.lower() == "exit":
                print("👋 Exiting...")
                break

            results = query(q, vectorizer, matrix, docs)

            if not results:
                print("❌ No answer found\n")
                continue

            print("\n📌 Answers:\n")

            for i, (text, score) in enumerate(results, 1):
                print(f"{i}. Confidence: {score:.2f}")
                print(text + "...\n")

    except KeyboardInterrupt:
        print("\n👋 Program stopped safely (Ctrl+C)")

if __name__ == "__main__":
    main()