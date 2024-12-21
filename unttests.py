import unittest
import os
import zipfile
import json
from unittest.mock import MagicMock
from emulator import ShellEmulator  # Замените 'your_module' на имя вашего файла

class TestShellEmulator(unittest.TestCase):

    def setUp(self):
        # Создаем временную директорию для виртуальной файловой системы
        os.makedirs("test_virtual_fs/test_dir", exist_ok=True)
        
        # Создаем тестовый файл
        with open("test_virtual_fs/test_file.txt", "w") as f:
            f.write("Hello World\n")
            f.write("Hello World\n")
            f.write("Goodbye World\n")

        # Создаем ZIP-файл из временной директории
        with zipfile.ZipFile("test_virtual_fs.zip", "w") as zipf:
            for root, dirs, files in os.walk("test_virtual_fs"):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join("test_virtual_fs")))

        # Создаем конфигурацию для эмулятора
        self.config = {
            "username": "test_user",
            "hostname": "test_host",
            "virtual_fs": "test_virtual_fs.zip"
        }

        # Создаем экземпляр эмулятора
        self.emulator = ShellEmulator(MagicMock(), self.config)

    def tearDown(self):
        # Удаляем временные файлы и директории после тестов
        import shutil
        shutil.rmtree("test_virtual_fs")
        if os.path.exists("test_virtual_fs.zip"):
            os.remove("test_virtual_fs.zip")

    def test_list_files(self):
        self.emulator.current_path = "/"
        output = self.emulator.list_files()
        self.assertIn("test_file.txt",output.strip())

    def test_change_directory(self):
        self.emulator.current_path = "/"
        self.emulator.change_directory("test_dir")
        self.assertEqual(self.emulator.current_path, "/")

    def test_uniq_file(self):
        self.emulator.current_path = "/home"
        
        output = self.emulator.uniq_file("hello.txt")
        self.assertEqual(output, "Hello World\nGoodbye World\n\n")

    def test_remove_file(self):
        self.emulator.current_path = "/test_dir"
        
        self.emulator.remove_file("test_file.txt")
        
        self.assertFalse(os.path.exists("test_virtual_fs/test_dir/test_file.txt"))

if __name__ == "__main__":
    unittest.main()
