from src.cleaner import convert_to_md, convert_to_json

convert_to_md("data/raw.txt", "data/skills.md")
print("✅ skills.md created successfully!")

convert_to_json("data/raw.txt", "data/skills.json")
print("✅ skills.json created successfully!")