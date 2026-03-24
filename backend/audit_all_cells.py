import pandas as pd
f = 'd:/Downloads2/syllabusmapper/backend/data/ECE_L0L5_VTU_CO_v2.xlsx'
df = pd.read_excel(f)

print(f"Columns: {df.columns.tolist()}")
found = False
for i, row in df.iterrows():
    for col, val in row.to_dict().items():
        sval = str(val)
        if '21EC' in sval or '21PHY' in sval:
            print(f"MATCH FOUND at Row {i}, Column {repr(col)}: {val}")
            print(f"Full Row {i}: {row.to_dict()}")
            found = True
            break
    if found: break

if not found:
    print("NO 21EC or 21PHY found in entire sheet!")
    # Print the absolute raw values of a few rows
    for i in range(5):
        print(f"Row {i} raw:", df.iloc[i].tolist())
