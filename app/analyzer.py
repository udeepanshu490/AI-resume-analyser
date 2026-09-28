import re

SKILLS = [
    "python","java","c","c++","c#","javascript","typescript","html","css","react",
    "node.js","fastapi","flask","django","sql","mysql","postgresql","mongodb",
    "git","github","docker","kubernetes","aws","azure","gcp","terraform",
    "pandas","numpy","scikit-learn","tensorflow","pytorch","machine learning",
    "deep learning","nlp","excel","power bi","tableau","statistics","rest api",
    "linux","github actions","ci/cd","data analysis","data visualization"
]

SECTION_PATTERNS = {
    "contact": ["email", "phone", "linkedin"],
    "summary": ["summary", "objective", "profile"],
    "skills": ["skills", "technical skills", "technologies"],
    "experience": ["experience", "work experience", "employment"],
    "education": ["education", "academic"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certification", "certifications", "certificate"]
}

def normalize(text):
    return re.sub(r"\s+", " ", text.lower())

def extract_skills(text):
    t = normalize(text)
    found = []
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9+#.-])" + re.escape(skill) + r"(?![a-z0-9+#.-])"
        if re.search(pattern, t):
            found.append(skill)
    return sorted(set(found))

def section_check(text):
    t = normalize(text)
    return {k: any(x in t for x in v) for k, v in SECTION_PATTERNS.items()}

def score_resume(text, skills):
    sections = section_check(text)
    score = 0
    score += min(len(skills) * 2.5, 30)
    score += sum(sections.values()) / len(sections) * 45
    word_count = len(text.split())
    if 250 <= word_count <= 900:
        score += 15
    elif 150 <= word_count < 250 or 900 < word_count <= 1300:
        score += 8
    else:
        score += 3
    if re.search(r"\b(20\d{2}|19\d{2})\b", text):
        score += 5
    if re.search(r"\b\d+%\b|\b\d+\+\b", text):
        score += 5
    return round(min(score, 100), 1)

def analyze(text):
    skills = extract_skills(text)
    sections = section_check(text)
    score = score_resume(text, skills)

    suggestions = []
    missing_sections = [k.title() for k, present in sections.items() if not present]
    if missing_sections:
        suggestions.append("Add missing sections: " + ", ".join(missing_sections) + ".")
    if len(skills) < 6:
        suggestions.append("Add more relevant technical skills and tools that you genuinely know.")
    if not re.search(r"\b\d+%\b|\b\d+\+\b", text):
        suggestions.append("Use measurable achievements such as percentages, counts, revenue, speed, or time saved.")
    if len(text.split()) < 250:
        suggestions.append("Your resume appears short; add relevant project, experience, and achievement details.")
    if not re.search(r"linkedin", text.lower()):
        suggestions.append("Consider adding a LinkedIn profile URL.")
    if not suggestions:
        suggestions.append("Good structure detected. Tailor keywords for each target job.")

    return {
        "score": score,
        "skills": skills,
        "sections": sections,
        "word_count": len(text.split()),
        "suggestions": suggestions
    }
