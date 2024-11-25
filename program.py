import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import csv
import json
from collections import defaultdict
import threading

# Задаем пароль
PASSWORD = "TrekMark"  # Установленный пароль

def check_password():
    password_window = tk.Toplevel(root)
    password_window.title("Введите пароль")

    tk.Label(password_window, text="Пароль:").pack(pady=10)
    password_entry = tk.Entry(password_window, show='*')
    password_entry.pack(pady=10)

    def verify_password():
        if password_entry.get() == PASSWORD:
            password_window.destroy()  # Закрываем окно, если пароль верный
            main_app()  # Запускаем основное приложение
        else:
            messagebox.showerror("Ошибка", "Неверный пароль!")
            password_window.destroy()
            root.quit()  # Закрываем приложение при неверном пароле

    tk.Button(password_window, text="Подтвердить", command=verify_password).pack(pady=10)

def main_app():
    # Создание главного окна
    global root
    root = tk.Tk()
    root.title("Поиск дублей в файлах")

    # Кнопка для выбора файлов
    select_button = tk.Button(root, text="Выбрать файлы", command=select_files)
    select_button.pack(pady=10)

    # Список выбранных файлов
    global file_list
    file_list = tk.Listbox(root, width=50, height=10)
    file_list.pack(pady=10)

    # Поле для ввода строк для исключения
    exclude_label = tk.Label(root, text="Строки для исключения (через запятую):")
    exclude_label.pack(pady=5)

    exclude_entry = tk.Entry(root, width=50)
    exclude_entry.pack(pady=5)

    # Поля для ввода минимальной и максимальной длины строк
    min_length_label = tk.Label(root, text="Минимальная длина строки:")
    min_length_label.pack(pady=5)

    min_length_entry = tk.Entry(root, width=10)
    min_length_entry.pack(pady=5)

    max_length_label = tk.Label(root, text="Максимальная длина строки:")
    max_length_label.pack(pady=5)

    max_length_entry = tk.Entry(root, width=10)
    max_length_entry.pack(pady=5)

    # Поле для игнорируемых символов
    ignore_label = tk.Label(root, text="Игнорируемые символы:")
    ignore_label.pack(pady=5)

    ignore_entry = tk.Entry(root, width=50)
    ignore_entry.pack(pady=5)

    # Настройки чувствительности к регистру
    ignore_case_var = tk.BooleanVar()
    ignore_case_check = tk.Checkbutton(root, text="Игнорировать регистр", variable=ignore_case_var)
    ignore_case_check.pack(pady=5)

    # Прогресс-бар
    global progress_bar
    progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
    progress_bar.pack(pady=10)

    # Кнопка для поиска дублей
    find_button = tk.Button(root, text="Найти дубликаты", command=find_duplicates)
    find_button.pack(pady=10)

    # Кнопка для очистки
    clear_button = tk.Button(root, text="Очистить", command=clear_all)
    clear_button.pack(pady=10)

    # Запуск главного цикла
    root.mainloop()

def select_files():
    files = filedialog.askopenfilenames(title="Выберите файлы", filetypes=(("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("JSON Files", "*.json"), ("All Files", "*.*")))
    if files:
        file_list.delete(0, tk.END)  # Очистить список
        for file in files:
            file_list.insert(tk.END, file)  # Добавить выбранные файлы в список

def find_duplicates():
    files = file_list.get(0, tk.END)  # Получаем список выбранных файлов
    if not files:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите файлы для анализа.")
        return

    progress_bar['maximum'] = len(files)
    progress_bar['value'] = 0
    root.update_idletasks()  # Обновляем интерфейс

    all_lines = defaultdict(int)  # Словарь для хранения строк и их количества
    duplicates = defaultdict(int)  # Словарь для хранения найденных дубликатов

    # Создаем и запускаем поток для поиска дубликатов
    thread = threading.Thread(target=process_files, args=(files, all_lines, duplicates))
    thread.start()

def process_files(files, all_lines, duplicates):
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                if file.endswith('.csv'):
                    reader = csv.reader(f)
                    lines = [row[0] for row in reader]  # Читаем только первый столбец
                elif file.endswith('.json'):
                    data = json.load(f)
                    lines = [str(item) for item in data]  # Преобразуем все элементы в строки
                else:
                    lines = f.readlines()  # Читаем все строки из файла

                for line in lines:
                    line = line.strip()
                    all_lines[line] += 1  # Увеличиваем счетчик для строки

            # Обновляем прогресс-бар
            progress_bar['value'] += 1
            root.update_idletasks()  # Обновляем интерфейс

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл {file}:\n{e}")
            return

    # Находим дубликаты
    for line, count in all_lines.items():
        if count > 1:
            duplicates[line] = count

    # Выводим результаты в основном потоке
    root.after(0, show_results, duplicates)

def show_results(duplicates):
    if duplicates:
        results = "\n".join([f"{line}: {count}" for line, count in duplicates.items()])
        messagebox.showinfo("Результаты", f"Найдены дубликаты:\n{results}")
        save_results(duplicates)  # Сохраняем результаты в файл
    else:
        messagebox.showinfo("Результаты", "Дубликаты не найдены.")

def save_results(duplicates):
    save_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if save_file:
        with open(save_file, 'w', encoding='utf-8') as f:
            for line, count in duplicates.items():
                f.write(f"{line}: {count}\n")
        messagebox.showinfo("Сохранение", "Результаты сохранены успешно.")

def clear_all():
    file_list.delete(0, tk.END)  # Очистить список файлов
    exclude_entry.delete(0, tk.END)  # Очистить поле исключаемых строк
    min_length_entry.delete(0, tk.END)  # Очистить поле минимальной длины
    max_length_entry.delete(0, tk.END)  # Очистить поле максимальной длины
    ignore_entry.delete(0, tk.END)  # Очистить поле игнорируемых символов
    progress_bar['value'] = 0  # Сбросить прогресс-бар

# Создаем главное окно
root = tk.Tk()
root.withdraw()  # Скрываем главное окно, пока не введен пароль

check_password()  # Запрашиваем пароль

# Запускаем главный цикл, если пароль введен правильно
root.mainloop()
