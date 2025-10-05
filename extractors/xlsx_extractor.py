import pandas as pd

def extract_xlsx(file_path):
    df_dict = pd.read_excel(file_path, sheet_name=None)  # all sheets
    text = ""
    for sheet_name, df in df_dict.items():
        text += f"\n[SHEET {sheet_name}]\n"
        sheet_text = " ".join(df.astype(str).fillna("").values.flatten())
        text += sheet_text
    return text