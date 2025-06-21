class SurveyEntry:
    def __init__(self, row):
        self.stt = row['STT']
        self.msbch = row['MSBCH']
        self.sdt = row['SDT']
        self.ten_dv = row['Tên DV']
        self.s4_head = row['S4: Head']
        self.gioi_tinh = row['Giới tính']
        self.tinh_song = row['S8: Tỉnh đang sống']
        self.q1 = row['Q1']
        self.q2_hai_long = row.get('Q2: Hài lòng', "")
        self.q2_chua_hai_long = row.get('Q2: Chưa Hài lòng', "")
        self.q3 = row.get('Q3', "")
        self.q4 = row.get('Q4', "")
        self.q5 = row.get('Q5', "")
        self.q6 = row.get('Q6', "")
        self.q7 = row.get('Q7', "")
        self.q8 = row.get('Q8', "")
        self.q9 = row.get('Q9', "")
        self.q10 = row.get('Q10', "")
        self.q12 = row.get('Q12', "")
        self.q13 = row.get('Q13', "")
        self.q15 = row.get('Q15', "")
    
    def __repr__(self):
        return f"<SurveyEntry STT={self.stt}, Tên={self.ten_dv}>"
