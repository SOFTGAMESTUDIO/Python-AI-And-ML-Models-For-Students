from extractor import extract_columns
from formatter import display_columns

def main():
    pdf_path = input("Enter PDF path: ")
    data = extract_columns(pdf_path)
    display_columns(data)

if __name__ == "__main__":
    main()