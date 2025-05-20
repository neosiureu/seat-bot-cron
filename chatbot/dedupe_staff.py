import os
import pandas as pd


def dedupe_excel(file_name="교직원전화번호.xlsx", overwrite=True):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    path = os.path.join(desktop, file_name)

    if not os.path.exists(path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

    df = pd.read_excel(path, engine="openpyxl")
    df_clean = df.drop_duplicates(keep="first").dropna(how="all")

    if overwrite:
        save_path = path
    else:
        root, ext = os.path.splitext(path)
        save_path = f"{root}_dedup{ext}"

    df_clean.to_excel(save_path, index=False, engine="openpyxl")
    print(f"저장 완료 → {save_path}  (행 수: {len(df_clean)})")


if __name__ == "__main__":
    dedupe_excel()
