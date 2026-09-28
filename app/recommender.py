from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend(resume_text, resume_skills, jobs, top_n=6):
    documents = [resume_text] + [j["description"] for j in jobs]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(documents)
    text_scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

    results = []
    resume_set = set(resume_skills)

    for i, job in enumerate(jobs):
        required = set(job["skills"])
        matched = sorted(resume_set & required)
        missing = sorted(required - resume_set)
        skill_score = len(matched) / max(len(required), 1)
        final_score = (text_scores[i] * 0.35 + skill_score * 0.65) * 100

        results.append({
            **job,
            "match": round(min(final_score, 100), 1),
            "matched_skills": matched,
            "missing_skills": missing
        })

    return sorted(results, key=lambda x: x["match"], reverse=True)[:top_n]
