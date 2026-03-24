import pandas as pd
import os

f = 'd:/Downloads2/syllabusmapper/backend/data/ECE_L0L5_VTU_CO_v2.xlsx'
df = pd.read_excel(f, header=None)

print(f"Total Rows: {len(df)}")
for i, row in df.iterrows():
    row_list = [str(x) for x in row.tolist()]
    # Look for something that looks like a course code or the header we expect
    joined = " ".join(row_list).lower()
    if 'skill description' in joined or 'course' in joined:
        print(f"Possible Header at row {i}:")
        print(row_list)
        # Check the NEXT row for data
        next_row = df.iloc[i+1].tolist()
        print(f"First data sample (row {i+1}):")
        print(next_row)
        break

# Also print the first 5 rows regardless
print("\nFIRST 5 ROWS RAW:")
for i in range(5):
    print(df.iloc[i].tolist())
