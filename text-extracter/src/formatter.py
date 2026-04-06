def display_columns(pages_data):
    for i, page in enumerate(pages_data, start=1):
        print("\n" + "=" * 60)
        print(f"PAGE {i}")
        print("=" * 60 + "\n")

        left = page["left"]
        right = page["right"]

        # Merge columns
        combined = left + right

        # Clean + format text
        formatted_text = []
        paragraph = ""

        for line in combined:
            line = line.strip()

            if not line:
                continue

            # If sentence ends → new paragraph
            if line.endswith(('.', '!', '?')):
                paragraph += " " + line
                formatted_text.append(paragraph.strip())
                paragraph = ""
            else:
                paragraph += " " + line

        # Add remaining text
        if paragraph:
            formatted_text.append(paragraph.strip())

        # Print nicely
        for para in formatted_text:
            print(para)
            print()  # spacing between paragraphs