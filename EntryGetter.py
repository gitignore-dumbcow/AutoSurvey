import pandas as pd
from SurveyEntry import SurveyEntry
import os

def load_entries(csv_url):
    # Đọc danh sách đã submit (nếu có)
    submitted_set = set()
    if os.path.exists("Submited.txt"):
        with open("Submited.txt", "r", encoding="utf-8") as f:
            submitted_set = set(line.strip() for line in f if line.strip())

    # Đọc toàn bộ dữ liệu từ Google Sheets, ép kiểu chuỗi
    df = pd.read_csv(csv_url, dtype=str)
    df.columns = df.columns.str.strip()

    # Loại bỏ NaN hoặc chuỗi rỗng trong cột "Tên DV"
    df = df[df["Tên DV"].notna()]                            # bỏ NaN
    df = df[df["Tên DV"].str.strip() != ""]                  # bỏ chuỗi rỗng

    # Bỏ các entry đã tồn tại trong submitted
    df_filtered = df[~df["Tên DV"].isin(submitted_set)]

    entries = []
    for _, row in df_filtered.iterrows():
        entry = SurveyEntry(row)
        entries.append(entry)

    return entries
