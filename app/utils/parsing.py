import re
AT_USERNAME = re.compile(r"@([A-Za-z0-9_]{5,})")


def extract_usernames(text: str) -> list[str]:
    if not text:
        return []
    return list(dict.fromkeys(AT_USERNAME.findall(text)))
