# Assemble ENCANTADA from three parts
parts = []

# Part 1: Ch 1-10 (skip the title line, we'll add our own header)
with open('book1-ch1-10.md', 'r') as f:
    text = f.read()
    # Remove the file header, keep from first chapter
    idx = text.find('## Chapter One')
    if idx >= 0:
        parts.append(text[idx:].rstrip())

# Part 2: Ch 11-20 (skip placeholder note)
with open('book1.md', 'r') as f:
    text = f.read()
    idx = text.find('## Chapter Eleven')
    if idx >= 0:
        parts.append(text[idx:].rstrip())

# Part 3: Ch 21-30 + Epilogue (skip file header)
with open('book1-act4-5.md', 'r') as f:
    text = f.read()
    idx = text.find('## Chapter 21')
    if idx < 0:
        idx = text.find('Chapter 21')
    if idx >= 0:
        parts.append(text[idx:].rstrip())

header = """# ENCANTADA
## Book 1 of A Moura's Claim
### by [Author Name]

*A monster romance rooted in Portuguese mythology*

---

"""

final = header + '\n\n---\n\n'.join(parts) + '\n'

with open('book1-final.md', 'w') as f:
    f.write(final)

print(f"Assembled {len(final)} chars, {len(final.split())} words")

# Count chapters
import re
chapters = re.findall(r'## Chapter\b', final)
print(f"Found {len(chapters)} chapter headings")
