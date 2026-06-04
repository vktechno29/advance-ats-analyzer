import re

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else ""

def extract_phone(text):
    match = re.search(r'(\+?\d[\d\s\-]{8,15})', text)
    return match.group(0).strip() if match else ""

def extract_linkedin(text):
    match = re.search(r'linkedin\.com/in/[A-Za-z0-9_-]+', text)
    return match.group(0) if match else ""

def extract_name(text):
    lines = text.split("\n")

    for line in lines[:5]:
        line = line.strip()

        if len(line) > 3 and len(line) < 50:
            if "@" not in line and "linkedin" not in line.lower():
                return line

    return ""