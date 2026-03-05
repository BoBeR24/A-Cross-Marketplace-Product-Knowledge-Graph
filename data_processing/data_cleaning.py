import re

def clean_text(to_clean):
    if not isinstance(to_clean, str):
        return to_clean
    # Substitute all non-printable ASCII characters(see: https://www.ascii-code.com/) with spaces(to avoid words junction).
    cleaned = re.sub(r'[^ -~]', " ", to_clean).strip()

    return cleaned

def clean_corrupted(text: str):
    if not isinstance(text, str) or len(text) == 0 :
        return ""

    text = text.strip()
    sp_number = text.count(' ')

    # if most of the text is spaces - consider it corrupted and replace with N/A
    if sp_number / len(text) > 0.6:
        return ""
    else:
        return text