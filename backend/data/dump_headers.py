import pandas as pd
import json
import os

paths = [
    'D:/Downloads2/skill_assessment_questions_complete.csv',
    'D:/Downloads2/skill_assessment_questions_v4 (2).csv'
]

for p in paths:
    try:
        if not os.path.exists(p):
            print(f"File not found: {p}")
            continue
        df = pd.read_csv(p, nrows=1)
        print(f"Headers for {p}:")
        print(json.dumps(list(df.columns), indent=2))
        print("-" * 20)
    except Exception as e:
        print(f"Error reading {p}: {e}")
