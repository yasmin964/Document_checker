import pytesseract
import os
import re
from pdf2image import convert_from_path

os.environ['TESSDATA_PREFIX'] = '/usr/local/share/tessdata/'
# Пути к tesseract и poppler
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r"C:\Users\hamza\poppler\poppler-24.08.0\Library\bin"

pdf_folder = "pdfs"
output_file = "pdf_text.txt"


def convert_pdf_to_images(pdf_path):
    return convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)


def detect_orientation(image):
    try:
        osd = pytesseract.image_to_osd(image, lang="rus+eng")
        angle_match = re.search(r'Rotate: (\d+)', osd)
        if angle_match:
            return int(angle_match.group(1))
    except:
        pass
    return 0 


def extract_text_from_images(images):
    text = ""
    for img in images:
        angle = detect_orientation(img)
        rotated = img.rotate(-angle, expand=True)
        page_text = pytesseract.image_to_string(rotated, lang="rus", config="--oem 3 --psm 6 -c "
                                                                                "preserve_interword_spaces=1")
        text += page_text
    return text


def clean_document_text(text):
    # Удаляем номера документов (но оставляем даты)
    text = re.sub(r'(?i)(номер|№|#)\s*[:\-]?\s*[0-9A-Za-z\-/]+', '', text)

    # Удаляем ИНН/КПП/ОГРН
    text = re.sub(r'(?i)(ИНН|КПП|ОГРН)\s*[:\-]?\s*[0-9]{5,15}', '', text)

    # Удаляем номера счетов (но оставляем суммы)
    text = re.sub(r'(?i)(счет|р\/с|сч\.)\s*[:\-]?\s*[0-9]{15,20}', '', text)

    # Удаляем названия организаций
    text = re.sub(r'(?i)(ООО|АО|ЗАО|ИП|ОАО)\s*[«"\']?[А-Яа-яЁёA-Za-z0-9\s]+[»"\']?', '', text)

    # Оставляем только строки, содержащие цифры
    lines = [line.strip() for line in text.split('\n')
             if line.strip() and re.search(r'\d', line)]

    return '\n'.join(lines)

def fix_ocr_mistakes(text):
    replacements = {
        'О': '0', 'о': '0', '○': '0', '◯': '0', '〇': '0',
        'З': '3', 'з': '3', 'Ż': '3', 'ż': '3',
        'Ч': '4', 'ч': '4',
        'б': '6', 'Б': '6',
        'Т': '7', 'т': '7',
        'В': '8', 'в': '8',
        'д': '9', 'Д': '9',
        'l': '1', 'I': '1', '|': '1', 'і': '1',
        'С': 'C', 'с': 'c',
        'Р': 'P', 'р': 'p',
        'Х': 'X', 'х': 'x',
        'А': 'A', 'а': 'a',
        'Е': 'E', 'е': 'e',
        'К': 'K', 'к': 'k',
        'М': 'M', 'м': 'm',
        'Н': 'H', 'н': 'h',
        'Т': 'T', 'т': 't',
        '—': '-', '–': '-', '―': '-',
        '…': '...', '⋯': '...',
        '“': '"', '”': '"', '«': '"', '»': '"',
        '‘': "'", '’': "'",
        '№': '#', 'N°': '#',
        '₽': 'руб', '€': 'EUR', '$': 'USD',
        ',': '.',  
    }

    for src, target in replacements.items():
        text = text.replace(src, target)
    return text



# Обработка всех PDF файлов
with open(output_file, 'w', encoding='utf-8') as out:
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, filename)
            print(f"Обработка файла: {pdf_path}")
            try:
                images = convert_pdf_to_images(pdf_path)
                raw_text = extract_text_from_images(images)
                cleaned_text = clean_document_text(raw_text)
                corrected_text = fix_ocr_mistakes(cleaned_text)

                out.write(f"\n==== {filename} ====\n")
                out.write(corrected_text + "\n")
            except Exception as e:
                print(f"Ошибка при обработке {filename}: {e}")

print(f"\n Текст сохранён в: {output_file}")

import pandas as pd


def extract_text_from_excel(file_path):
    df = pd.read_excel(file_path)

    text_lines = []

    for index, row in df.iterrows():
        line = ' '.join([str(val) for val in row if pd.notnull(val)])
        if any(char.isdigit() for char in line):
            text_lines.append(line)

    return '\n'.join(text_lines)


# пример использования
excel_path = "тест.xls"
excel_text = extract_text_from_excel(excel_path)


with open("excel_text.txt", "w", encoding="utf-8") as f:
    f.write(excel_text)




