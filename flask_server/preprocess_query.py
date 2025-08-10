import re
import string

# Basic English and Chinese stopwords
EN_STOPWORDS = set([
    "the", "a", "an", "is", "at", "on", "in", "of", "to", "and", "for", "with", "this", "that"
])
CN_STOPWORDS = set([
    "的", "了", "是", "我", "想要", "买", "需要", "在", "一台", "一个"
])

# Simple spelling correction rules
SPELL_FIX_DICT = {
    "iphon": "iphone",
    "lapptop": "laptop",
    "celphone": "cellphone",
    "moblie": "mobile",
    "notbook": "notebook",
    "phne": "phone"
}

# Mapping of full-width to half-width punctuation
PUNCT_TRANSLATION = str.maketrans(
    "，。！？【】（）％＃＠＆１２３４５６７８９０",
    ",.!?[]()%#@&1234567890"
)

def remove_html(text: str) -> str:
    """Remove HTML tags"""
    return re.sub(r"<[^>]*>", "", text)

def normalize_punctuation(text: str) -> str:
    """Convert full-width punctuation to half-width"""
    return text.translate(PUNCT_TRANSLATION)

def lowercase_text(text: str) -> str:
    """Convert to lowercase"""
    return text.lower()

def correct_spelling(text: str) -> str:
    """Apply simple rule-based spelling correction"""
    for typo, correct in SPELL_FIX_DICT.items():
        text = re.sub(rf"\b{typo}\b", correct, text)
    return text

def remove_stopwords(text: str) -> str:
    """Remove predefined English and Chinese stopwords"""
    words = re.findall(r"\b\w+\b|[\u4e00-\u9fff]", text)
    filtered = [word for word in words if word not in EN_STOPWORDS and word not in CN_STOPWORDS]
    return " ".join(filtered)

def clean_whitespace(text: str) -> str:
    """Remove redundant spaces"""
    return re.sub(r"\s+", " ", text).strip()

def preprocess_query(query: str) -> str:
    """Main function to clean and normalize the user query"""
    query = remove_html(query)
    query = normalize_punctuation(query)
    query = lowercase_text(query)
    query = correct_spelling(query)
    query = clean_whitespace(query)
    query = remove_stopwords(query)
    return query
