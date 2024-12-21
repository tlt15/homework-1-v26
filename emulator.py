import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import zipfile
import json
import argparse

class ShellEmulator:
    def __init__(self, master, config):
        self.master = master
        self.master.title("Shell Emulator")
        self.current_path = "/"
        self.history = []

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.username = config['username']
        self.hostname = config['hostname']
        self.virtual_fs_path = config['virtual_fs']

        self.label = tk.Label(master, text=f"{self.username}@{self.hostname}")
        self.label.pack(padx=10, pady=5)

        self.entry = tk.Entry(master)
        self.entry.pack(padx=10, pady=10, fill=tk.X)
        self.entry.bind("<Return>", self.execute_command)

        # Создаем временную директорию для виртуальной файловой системы
        os.makedirs("virtual_fs", exist_ok=True)
        self.extract_virtual_fs()

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(description='Запуск эмулятора командной строки.')
        parser.add_argument('config', type=str, help='Путь к конфигурационному файлу (JSON).')
        
        args = parser.parse_args()
        
        if not os.path.exists(args.config):
            parser.error(f"Файл конфигурации '{args.config}' не найден.")
        
        return args

    def extract_virtual_fs(self):
        if not os.path.exists(self.virtual_fs_path):
            messagebox.showerror("Ошибка", "Файл виртуальной файловой системы не найден.")
            return

        with zipfile.ZipFile(self.virtual_fs_path) as zip_ref:
            zip_ref.extractall("virtual_fs")

    def execute_command(self, event):
        command = self.entry.get().strip()  # Удаляем лишние пробелы
        self.history.append(command)

        command_dict = {
            "ls": self.list_files,
            "cd": lambda: self.change_directory(command[3:]),
            "pwd": self.print_working_directory,
            "exit": self.master.quit,
            "du": self.disk_usage,
            "uniq": lambda: self.uniq_file(command[5:].strip()),  # Изменено на 5
            "rm": lambda: self.remove_file(command[3:].strip())
        }

        cmd_func = command_dict.get(command.split()[0], None)

        if cmd_func:
            cmd_func()
        else:
            self.text_area.insert(tk.END, f"{self.username}: команда не найдена\n")

    def list_files(self):
        try:
            files = os.listdir(f"virtual_fs{self.current_path}")
            output = "\n".join(files) if files else "Пустая директория\n"
            self.text_area.insert(tk.END, f"{output}\n")
            return output
        except FileNotFoundError:
            self.text_area.insert(tk.END, "Директория не найдена\n")
            return "Директория не найдена\n"

    def change_directory(self, path):
        if path == "..":
            if self.current_path != "/":
                parts = self.current_path.split("/")
                parts.pop()  
                self.current_path = "/".join(parts) or "/"
                return
            
        new_path = os.path.join(f"virtual_fs{self.current_path}", path)
        
        if os.path.isdir(new_path):
            self.current_path = new_path.replace("virtual_fs", "")
            return
        else:
            self.text_area.insert(tk.END, "Директория не найдена\n")

    def print_working_directory(self):
        current_dir = f"{self.username}@{self.hostname}:{self.current_path}\n"
        self.text_area.insert(tk.END, current_dir)

    def disk_usage(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(f"virtual_fs{self.current_path}"):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        
        self.text_area.insert(tk.END, f"Используемое пространство: {total_size} байт\n")

    def uniq_file(self, filename):
        filename = filename.strip()  # Удаляем лишние пробелы
        if not filename:
            self.text_area.insert(tk.END, "Имя файла не может быть пустым\n")
            return

        file_path = os.path.join(f"virtual_fs{self.current_path}", filename)

        try:
            with open(file_path) as file:
                lines = file.readlines()
                unique_lines = set(lines)
                output = ''.join(unique_lines)
                self.text_area.insert(tk.END, f"{output}\n")
                return f"{output}\n"
        except FileNotFoundError:
            self.text_area.insert(tk.END, f"Файл '{filename}' не найден по пути '{file_path}'\n")
            return f"Файл '{filename}' не найден по пути '{file_path}'\n"


    def remove_file(self, filename):
        try:
            file_path = os.path.join(f"virtual_fs{self.current_path}", filename.strip())
            os.remove(file_path)
            self.text_area.insert(tk.END, f"Файл '{filename}' удален.\n")
        except FileNotFoundError:
            self.text_area.insert(tk.END, "Файл не найден\n")
    
if __name__ == "__main__":
    args = ShellEmulator.parse_arguments()
    
    with open(args.config) as config_file:
        config = json.load(config_file)
    
    root = tk.Tk()
    app = ShellEmulator(root, config)

    root.mainloop()
