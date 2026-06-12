RESPONSES = {
    "docker": "Docker dong goi ung dung va dependencies vao container de chay nhat quan.",
    "cloud": "Cloud cung cap ha tang de ung dung co the truy cap qua Internet va scale de dang.",
    "redis": "Redis la kho du lieu trong bo nho, phu hop cho cache, session va rate limiting.",
}


def ask(question: str) -> str:
    normalized = question.lower()
    for keyword, response in RESPONSES.items():
        if keyword in normalized:
            return response
    return f"Simple agent received your question: {question}"
