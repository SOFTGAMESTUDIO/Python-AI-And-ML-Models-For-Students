def load_md(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by headings properly
    sections = content.split("## ")

    docs = []
    for sec in sections:
        sec = sec.strip()
        if len(sec) > 50:
            docs.append(sec)

    return docs