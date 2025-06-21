import tkinter as tk
from tkinter import scrolledtext

class LoggerWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Log hành vi khảo sát")
        self.root.geometry("600x400")
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Consolas", 10))
        self.text_area.pack(expand=True, fill='both')
        self.text_area.configure(state='disabled')

    def log(self, message):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.text_area.configure(state='disabled')

    def start(self):
        self.root.mainloop()
