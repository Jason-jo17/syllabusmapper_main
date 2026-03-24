import pandas as pd
f = 'd:/Downloads2/syllabusmapper/backend/data/ECE_L0L5_VTU_CO_v2.xlsx'
df = pd.read_excel(f)
for i, row in df.iterrows():
    if 'EC' in str(row.get('Secondary\nCode', '')):
        print(f"Row {i} Secondary Code:", row['Secondary\nCode'])
        print(f"Row {i} Secondary CO:", row.get('Secondary\nCO'))
    if i > 20: break
