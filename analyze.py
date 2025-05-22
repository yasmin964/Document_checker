import requests
import json
from pathlib import Path

API_KEY = "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"
MODEL = "deepseek/deepseek-r1:free"


def load_text_files():
    file1 = Path('excel_text.txt').read_text(encoding='utf-8')
    file2 = Path('pdf_text.txt').read_text(encoding='utf-8')
    return file1, file2


def prepare_prompt(excel_text, pdf_text):
    return f"""
Сравни данные, полученные из Excel-файла и PDF-документа. Это один и тот же документ, но они могли быть заполнены вручную. Найди отличия.

Excel-документ:
{excel_text}

PDF-документ:
{pdf_text}

Проанализируй:
1. Совпадают ли суммы, НДС и итоги? (Пройдись по всем документам и ответь Да/Нет)
2. Совпадают ли ИНН продавцов?
3. Совпадают ли даты и время?
4. Есть ли пропущенные строки или лишние?
5. Есть ли явные ошибки?

Выведи различия в виде таблицы или списка. Сделай итоговый вывод.
"""


def process_content(content):
    return content.replace('<think>', '').replace('</think>', '')


def chat_stream(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    with requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True
    ) as response:
        if response.status_code != 200:
            print("Ошибка API:", response.status_code)
            return ""

        full_response = []

        for chunk in response.iter_lines():
            if chunk:
                #  преобразует байты в обычную строку, используя кодировку utf-8.(Потому что почти все современные API и текстовые потоки используют UTF-8 — она поддерживает любые символы (включая русский язык, эмодзи и т.д.).)
                #  удаляет префикс data:
                chunk_str = chunk.decode('utf-8').replace('data: ', '')
                try:
                    chunk_json = json.loads(chunk_str)
                    if "choices" in chunk_json:
                        # Извлечение текста из структуры ответа дипсика
                        content = chunk_json["choices"][0]["delta"].get("content", "")
                        # очистка и печать
                        if content:
                            cleaned = process_content(content)
                            print(cleaned, end='', flush=True)
                            full_response.append(cleaned)
                except:
                    pass

        print()
        # вывод в 1 строку
        return ''.join(full_response)


def main():
    print("Загрузка и анализ документов...\n")

    # Загружаем тексты документов
    text1, text2 = load_text_files()

    # Формируем промт для анализа
    prompt = prepare_prompt(text1, text2)

    print("DeepSeek-R1 анализирует документы:", end='\n\n', flush=True)
    analysis_result = chat_stream(prompt)

    # Сохраняем результат анализа
    with open('analysis_result.txt', 'w', encoding='utf-8') as f:
        f.write(analysis_result)

    print("\nАнализ завершен. Результат сохранен в analysis_result.txt")


if __name__ == "__main__":
    main()