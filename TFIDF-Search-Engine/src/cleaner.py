import re
import json

def split_by_heading(text):
    # Split using known headings
    topics = re.split(
        r'(What is Python.*?|What is Artificial Intelligence.*?|What is Machine Learning.*?|TF-IDF.*?|How Python is Used.*?|How AI.*?)',
        text
    )

    docs = []

    for i in range(1, len(topics), 2):
        title = topics[i].strip()
        content = topics[i+1].strip() if i+1 < len(topics) else ""

        docs.append(f"{title}\n{content}")

    return docs


def get_structured_data(text):
    topics = re.split(
        r'(What is Python.*?|What is Artificial Intelligence.*?|What is Machine Learning.*?|TF-IDF.*?|How Python is Used.*?|How AI.*?)',
        text
    )

    data = []
    for i in range(1, len(topics), 2):
        title = topics[i].strip()
        content = topics[i+1].strip() if i+1 < len(topics) else ""
        data.append({
            "title": title,
            "content": content
        })
    return data


def convert_to_md(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    docs = split_by_heading(text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 📘 AI Knowledge Base\n\n")

        for doc in docs:
            title = doc.split("\n")[0]

            f.write(f"## {title}\n")
            f.write(doc + "\n\n")


def convert_to_json(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    data = get_structured_data(text)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)