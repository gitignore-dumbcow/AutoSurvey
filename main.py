import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import threading
from EntryGetter import load_entries
from LoggerWindow import LoggerWindow
from AutoSurveyor import run_survey

class SurveyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Khảo sát tự động")

        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.result_text = tk.StringVar()
        self.progress_text = tk.StringVar()
        self.remaining_time = tk.StringVar()
        self.progress_percent = tk.DoubleVar()
        self.logger = None
        self.selected_entries = []

        self.build_ui()

    def build_ui(self):
        title = tk.Label(self.root, text="KHẢO SÁT TỰ ĐỘNG", font=("Arial", 20, "bold"))
        title.pack(pady=10)

        frame_inputs = tk.Frame(self.root)
        frame_inputs.pack()


        tk.Button(frame_inputs, text="Tìm kiếm", command=self.fetch_entries).grid(row=0, column=4, padx=10)

        self.listbox = tk.Listbox(self.root, width=50)
        self.listbox.pack(pady=5)

        self.info_label = tk.Label(self.root, text="", fg="blue")
        self.info_label.pack()

        frame_controls = tk.Frame(self.root)
        frame_controls.pack(pady=10)

        tk.Button(frame_controls, text="Bắt đầu", command=self.start_survey).grid(row=0, column=1, padx=10)

        self.progress_bar = ttk.Progressbar(self.root, length=400, variable=self.progress_percent)
        self.progress_bar.pack(pady=5)

        self.status_label = tk.Label(self.root, textvariable=self.progress_text)
        self.status_label.pack()
        self.time_label = tk.Label(self.root, textvariable=self.remaining_time)
        self.time_label.pack()

    def fetch_entries(self):
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSDjpvUxoIRxdLyyjVv4-l59wH36tj4DMx3Lh8nw_sWlQHo1SjlRTlXQBkoS9VZy_oOn6LyaJVHaMav/pub?output=csv"
        try:
            entries = load_entries(csv_url)
        except Exception as e:
            self.listbox.delete(0, tk.END)
            self.listbox.insert(tk.END, f" ▲ Lỗi tải dữ liệu: {e}")
            return

        self.selected_entries = entries
        self.listbox.delete(0, tk.END)

        for i, e in enumerate(self.selected_entries, start=1):
            self.listbox.insert(tk.END, f"{i}. {e.ten_dv}")
        
        self.info_label.config(text=f"Tìm thấy {len(self.selected_entries)} mục chưa được submit.")


    def start_survey(self):
        if self.selected_entries == []:
            self.info_label.config(text=" ▲ Bạn cần tìm kiếm trước khi bắt đầu.")
            return
        
        total = len(self.selected_entries)
        

        self.logger = LoggerWindow()

        def update_progress(done, total):
            percent = done / total * 100
            self.progress_percent.set(percent)
            self.progress_text.set(f"Đã xử lý: {done}/{total}")

        def run_in_thread():
            try:
                run_survey(self.logger, self.selected_entries, submit=True, progress_callback=lambda d, t: self.root.after(0, update_progress, d, t))
            except Exception as e:
                self.root.after(0, lambda: self.logger.log(f"[LỖI] Đã xảy ra lỗi trong quá trình khảo sát:\n{e}"))
                self.root.after(0, lambda: self.info_label.config(text="❌ Có lỗi xảy ra khi khảo sát."))

        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()

        self.logger.start()




# Khởi chạy ứng dụng
if __name__ == "__main__":
    root = tk.Tk()
    app = SurveyApp(root)
    root.mainloop()
