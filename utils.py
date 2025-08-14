def is_safe(text):
    banned_words = ["hate", "violence"]
    for word in banned_words:
        if word in text.lower():
            return False
    return True