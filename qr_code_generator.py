import qrcode
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, Canvas, filedialog, messagebox, colorchooser, Frame
from PIL import Image, ImageTk


# Глобальные переменные
qr_image = None


# Функция для создания данных vCard или другой структуры
def create_text_data():
    """
    Собирает данные из дополнительных полей при выборе 'Текст'
    и формирует vCard для QR-кода.
    """
    name = fio_field.get()
    phone1 = phone1_field.get()
    phone2 = phone2_field.get()
    email = email_field.get()
    telegram = telegram_field.get()

    # Формируем vCard
    vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
"""
    if phone1:
        vcard += f"TEL;TYPE=WORK,VOICE:{phone1}\n"
    if phone2:
        vcard += f"TEL;TYPE=CELL:{phone2}\n"
    if email:
        vcard += f"EMAIL:{email}\n"
    if telegram:
        vcard += f"X-SOCIALPROFILE;TYPE=Telegram:{telegram}\n"
    vcard += "END:VCARD"
    return vcard


# Функция генерации QR-кода
def generate_qr():
    global qr_image
    data_type = selected_type.get()

    qr_data = ""

    if data_type == "Текст":
        qr_data = create_text_data()
    elif data_type == "URL":
        qr_data = input_field.get()
    elif data_type == "Email":
        qr_data = f"mailto:{input_field.get()}"
    elif data_type == "Локация":
        try:
            lat, lon = map(str.strip, input_field.get().split(","))
            qr_data = f"geo:{lat},{lon}"
        except ValueError:
            messagebox.showerror("Ошибка", "Введите координаты в формате 'широта, долгота'")
            return
    elif data_type == "Wi-Fi":
        ssid = wifi_ssid.get()
        password = wifi_password.get()
        if not ssid or not password:
            messagebox.showerror("Ошибка", "Введите SSID и пароль!")
            return
        qr_data = f"WIFI:T:WPA;S:{ssid};P:{password};;"

    if not qr_data:
        messagebox.showerror("Ошибка", "Введите данные для генерации QR-кода!")
        return

    # Генерация QR-кода
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Создаём изображение QR-кода с кастомизацией
    img = qr.make_image(fill_color=fill_color.get(), back_color=bg_color.get())

    # Сохранение и предварительный просмотр
    img.save("qrcode.png")
    qr_image = img
    preview_qr()


# Предварительный просмотр QR-кода
def preview_qr():
    img_preview = qr_image.resize((200, 200))
    img_preview = ImageTk.PhotoImage(img_preview)
    qr_canvas.create_image(100, 100, image=img_preview)
    qr_canvas.image = img_preview


# Сохранение QR-кода
def save_qr():
    if not qr_image:
        messagebox.showerror("Ошибка", "Сначала сгенерируйте QR-код!")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        qr_image.save(file_path)
        messagebox.showinfo("Сохранено", f"QR-код сохранён в {file_path}")


# Выбор цветов
def choose_color(option):
    color = colorchooser.askcolor()[1]
    if color:
        if option == "fill":
            fill_color.set(color)
        elif option == "bg":
            bg_color.set(color)


# Показать или скрыть дополнительные поля
def toggle_fields(*args):
    if selected_type.get() == "Текст":
        text_fields_frame.pack(pady=10)
        input_field.pack_forget()
        wifi_frame.pack_forget()
    elif selected_type.get() == "Wi-Fi":
        wifi_frame.pack(pady=5)
        input_field.pack_forget()
        text_fields_frame.pack_forget()
    else:
        input_field.pack(pady=5)
        wifi_frame.pack_forget()
        text_fields_frame.pack_forget()


# Основное окно
app = Tk()
app.title("QR Code Generator")
app.geometry("600x800")
app.resizable(False, False)

# Выбор типа данных
Label(app, text="Тип данных:").pack(pady=5)
selected_type = StringVar(app)
selected_type.set("Текст")
data_types = ["Текст", "URL", "Email", "Локация", "Wi-Fi"]
OptionMenu(app, selected_type, *data_types).pack()

# Поле ввода
Label(app, text="Введите данные:").pack(pady=5)
input_field = Entry(app, width=50)
input_field.pack(pady=5)

# Поля для Wi-Fi
wifi_ssid = StringVar()
wifi_password = StringVar()
wifi_frame = Canvas(app)
Label(wifi_frame, text="SSID:").grid(row=0, column=0, padx=5, pady=5)
Entry(wifi_frame, textvariable=wifi_ssid, width=20).grid(row=0, column=1, padx=5, pady=5)
Label(wifi_frame, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
Entry(wifi_frame, textvariable=wifi_password, width=20).grid(row=1, column=1, padx=5, pady=5)

# Дополнительные поля для "Текст"
text_fields_frame = Frame(app)
Label(text_fields_frame, text="ФИО:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
fio_field = Entry(text_fields_frame, width=30)
fio_field.grid(row=0, column=1, padx=5, pady=5)

Label(text_fields_frame, text="Телефон 1:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
phone1_field = Entry(text_fields_frame, width=30)
phone1_field.grid(row=1, column=1, padx=5, pady=5)

Label(text_fields_frame, text="Телефон 2:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
phone2_field = Entry(text_fields_frame, width=30)
phone2_field.grid(row=2, column=1, padx=5, pady=5)

Label(text_fields_frame, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
email_field = Entry(text_fields_frame, width=30)
email_field.grid(row=3, column=1, padx=5, pady=5)

Label(text_fields_frame, text="Telegram:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
telegram_field = Entry(text_fields_frame, width=30)
telegram_field.grid(row=4, column=1, padx=5, pady=5)

# Цвета QR-кода
fill_color = StringVar(value="black")
bg_color = StringVar(value="white")
Button(app, text="Цвет QR-кода", command=lambda: choose_color("fill")).pack(pady=5)
Button(app, text="Цвет фона", command=lambda: choose_color("bg")).pack(pady=5)

# Кнопки
Button(app, text="Сгенерировать QR-код", command=generate_qr).pack(pady=10)
Button(app, text="Сохранить QR-код", command=save_qr).pack(pady=10)

# Полотно для отображения QR-кода
qr_canvas = Canvas(app, width=200, height=200, bg="white")
qr_canvas.pack(pady=10)

# Обработчик изменения типа данных
selected_type.trace("w", toggle_fields)

# Запуск приложения
app.mainloop()
