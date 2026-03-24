import pandas as pd
import json

def debug():
    f1 = 'd:/Downloads2/syllabusmapper/backend/data/Event Mastersheet mockup - CO sheet.csv'
    f2 = 'd:/Downloads2/syllabusmapper/backend/data/Event Mastersheet mockup - Domain, skillset L C (9).csv'
    
    print("Checking CO CSV...")
    df1 = pd.read_csv(f1)
    print("CO COLS:", df1.columns.tolist())
    print("CO ROW 0:", df1.iloc[0].to_dict())
    
    print("\nChecking SKILL CSV...")
    df2 = pd.read_csv(f2)
    print("SKILL RAW COLS:", df2.columns.tolist())
    for i, row in df2.iterrows():
        if not pd.isna(row.get('Domain')):
            print(f"Data starts at index {i}")
            print("First data row:", row.to_dict())
            break
            
if __name__ == "__main__":
    debug()
