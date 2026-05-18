from datetime import datetime, timedelta

def calculate_cs(level, session_count, prev_score):
    u_score = (level / 5) * 100
    r_score = min(100, session_count * 15)
    if session_count <= 1:
        score = (u_score * 0.75 + r_score * 0.25)
    else:
        score = (u_score * 0.60 + r_score * 0.25 + prev_score * 0.15)
    return round(min(100, max(0, score)), 1)

def get_next_review(score):
    days = 7 if score >= 80 else (3 if score >= 60 else (1 if score >= 40 else 0))
    return (datetime.now() + timedelta(days=days)).isoformat()
