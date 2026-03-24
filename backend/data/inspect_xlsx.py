import pandas as pd
import sys

def list_sheets(path):
    try:
        xl = pd.ExcelFile(path)
        print(f"Sheet Names: {xl.sheet_names}")
        for sheet in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet, nrows=5)
            print(f"\nSheet: {sheet}")
            print(f"Columns: {df.columns.tolist()}")
            print(df.head(2).to_json(orient='records', indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_sheets("d:/Downloads2/syllabusmapper/backend/data/ECE_L0L5_VTU_CO_v2.xlsx")
