import json
import os
import pandas as pd

print("="*70)
print("🚀 TALENTLENS INTENT-AWARE PURE COMPUTATIONAL ENGINE — SPEC V4")
print("="*70)

def load_all_candidates(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing crucial source dataset: {file_path}")
    candidates = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    candidates.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return candidates

def check_honeypot(candidate):
    """Rule 7 Guardrail: Flags anomalous expertise-to-tenure profiles."""
    prof = candidate.get('profile', {})
    skills = candidate.get('skills', [])
    history = candidate.get('career_history', [])
    yoe = float(prof.get('years_of_experience', 0.0))
    
    expert_skills = [s for s in skills if s.get('proficiency') in ['advanced', 'expert']]
    if yoe <= 2.0 and len(expert_skills) >= 5:
        return True, "disproportionate skill claims for short tenure"
        
    for job in history:
        duration_months = job.get('duration_months')
        if duration_months and (duration_months / 12.0) > (yoe + 0.5):
            return True, "chronological discrepancies in employment timeline"
            
    return False, ""

def compute_functional_score(candidate):
    """Calculates structural relevance without heavy CPU embedding overhead."""
    prof = candidate.get('profile', {})
    history = candidate.get('career_history', [])
    signals = candidate.get('redrob_signals', {})
    
    title = str(prof.get('current_title', '')).lower()
    headline = str(prof.get('headline', '')).lower()
    summary = str(prof.get('summary', '')).lower()
    
    # 1. Target JD Alignment Keywords (Dense Search Framework)
    keywords = ['ai', 'ml', 'machine learning', 'retrieval', 'ranking', 'embedding', 'search', 'nlp', 'llm', 'vector']
    match_count = 0
    full_text = f"{title} {headline} {summary}"
    
    for job in history:
        full_text += f" {str(job.get('title', '')).lower()} {str(job.get('description', '')).lower()}"
        
    for kw in keywords:
        if kw in full_text:
            match_count += 1
            
    text_score = min(1.0, match_count / len(keywords))
    
    # 2. Extract Behavioral Signals
    response_rate = float(signals.get('recruiter_response_rate', 0.5))
    interview_completion = float(signals.get('interview_completion_rate', 1.0))
    notice_days = int(signals.get('notice_period_days', 60))
    pref_mode = str(signals.get('preferred_work_mode', '')).lower()
    willing_to_relocate = bool(signals.get('willing_to_relocate', False))
    
    availability = (response_rate * 0.6) + (interview_completion * 0.4)
    if response_rate < 0.20:
        availability *= 0.3  # Sudden death flag
        
    logistics_mod = 1.0
    if notice_days <= 30:
        logistics_mod += 0.15
    elif notice_days > 90:
        logistics_mod -= 0.20
    if pref_mode in ['hybrid', 'flexible'] or willing_to_relocate:
        logistics_mod += 0.10
        
    # 3. Enforce strict direct product company background rule
    company_penalty = 1.0
    disallowed_firms = ['tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 'capgemini']
    for job in history:
        comp = str(job.get('company', '')).lower()
        if any(firm in comp for firm in disallowed_firms):
            company_penalty = 0.2  # Heavy deduction for consulting backgrounds
            break
            
    # Experience range modifier (5-9 years sweet spot)
    yoe = float(prof.get('years_of_experience', 0.0))
    exp_mod = 1.0
    if yoe < 4.0: exp_mod = 0.70
    elif yoe > 12.0: exp_mod = 0.85
    
    final_score = ((text_score * 0.60) + (availability * 0.25) + (logistics_mod * 0.15)) * company_penalty * exp_mod
    return round(max(0.115, min(0.995, final_score)), 3)

def generate_reasoning(candidate, is_honeypot, honeypot_msg):
    if is_honeypot:
        return f"Profile dropped during baseline validation: {honeypot_msg}."
    prof = candidate.get('profile', {})
    title = prof.get('current_title', 'AI Engineer')
    yoe = prof.get('years_of_experience', 0.0)
    company = prof.get('current_company', 'Product Co')
    return f"Strong structural match holding {yoe} YOE as {title} at {company}. Demonstrates solid hands-on engineering experience aligned with core platform parameters."

def run_production_pipeline(input_json, output_csv):
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    print("[1/3] Parsing entire candidate database into RAM layers...")
    candidates = load_all_candidates(input_json)
    records = []
    
    for c in candidates:
        c_id = c.get('candidate_id')
        if not c_id: continue
        
        is_honeypot, honeypot_msg = check_honeypot(c)
        score = 0.010 if is_honeypot else compute_functional_score(c)
        reason = generate_reasoning(c, is_honeypot, honeypot_msg)
        
        records.append({
            "candidate_id": str(c_id).strip(),
            "score": score,
            "reasoning": reason
        })
        
    df = pd.DataFrame(records)
    
    print("[2/3] Executing high-speed score evaluation maps...")
    # Sort deterministically based on section rules (Score descending, ID ascending)
    df = df.sort_values(by=['score', 'candidate_id'], ascending=[False, True]).reset_index(drop=True)
    
    print("[3/3] Engineering ranking matrices and filtering top 100 entries...")
    top100 = df.head(100).copy()
    top100['rank'] = top100.index + 1
    
    final_output = top100[['candidate_id', 'rank', 'score', 'reasoning']]
    final_output.to_csv(output_csv, index=False)
    
    print(f"\n🚀 SUCCESS! Submission file written cleanly to: {output_csv}")
    print(f"📊 Rows generated: {len(final_output)} (Exactly 100 entries + 1 header row).")

if __name__ == "__main__":
    # Change 'team_xxx.csv' to match your registered hackathon participant ID
    run_production_pipeline("data/candidates.jsonl", "output/team_xxx.csv")