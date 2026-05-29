import os
import logging
import matplotlib.pyplot as plt
from openai import OpenAI

logging.basicConfig(
    filename="main_logs.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding="utf-8"
)

def get_api_key(config_path="config.txt"):
    if not os.path.exists(config_path):
        logging.critical(f"Файл конфигурации {config_path} не найден!")
        return ""
    
    with open(config_path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        
        if "DEEPSEEK_API_KEY=" in first_line:
            logging.info(f"Файл конфигурации {config_path} успешно прочитан.")
            parts = first_line.split("=")
            return parts[1].strip()
            
    logging.error("В первой строке конфигурационного файла не найден ключ DEEPSEEK_API_KEY=")
    return ""

def load_reviews(file_path="reviews.csv"):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден")
            
        reviews = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.strip()
                if clean_line:  
                    reviews.append(clean_line)
                    
        logging.info(f"Успешно загружено {len(reviews)} отзывов.")
        return reviews
        
    except Exception as e:
        logging.error(f"Ошибка при чтении файла {file_path}: {e}")
        return []

def analyze_review(client, text, idx):
    prompt = f"""
    Проанализируй отзыв о ресторане. Тебе нужно определить оценку отзыва от 0 до 10 и его главную категорию.
    Доступные категории строго: Кухня, Обслуживание, Интерьер, Цены.

    Выведи ответ СТРОГО в формате "Число:Категория" без пробелов, лишних слов и точек.
    Пример ответа: 9:Кухня

    Отзыв: "{text}"
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        
        response_text = response.choices[0].message.content.strip()
        
        if ":" in response_text:
            parts = response_text.split(":")
            score_str = parts[0].strip()
            category = parts[1].strip().replace(".", "").capitalize()
            
            if score_str.isdigit():
                score = int(score_str)
            else:
                score = 5
            
            valid_categories = ["Кухня", "Обслуживание", "Интерьер", "Цены"]
            if category not in valid_categories:
                category = "Кухня"
                
            logging.info(f"Отзыв номер {idx} проанализирован:  {score}:{category}.")
            return score, category
        
        logging.warning(f"Некорректный формат от ИИ на отзыве номер {idx}: '{response_text}'. По умолчанию выставленно значение 5, Кухня.")
        return 5, "Кухня"
        
    except Exception as error:
        logging.error(f"Сбой при запросе к API на отзыве №{idx}: {error}")
        return 5, "Кухня"
    

def draw_dashboard(results):
    if not results:
        logging.warning("Нет данных для построения графиков.")
        return

    logging.info("Данные переданы в Matplotlib.")

    counts = {}
    for item in results:
        score = item["score"]
        counts[score] = counts.get(score, 0) + 1
            
    sorted_scores = sorted(counts.keys())
    pie_labels = [f"Балл {s} ({counts[s]} шт.)" for s in sorted_scores]
    pie_sizes = [counts[s] for s in sorted_scores]

    categories = ["Кухня", "Обслуживание", "Интерьер", "Цены"]
    sums = {"Кухня": 0, "Обслуживание": 0, "Интерьер": 0, "Цены": 0}
    amounts = {"Кухня": 0, "Обслуживание": 0, "Интерьер": 0, "Цены": 0}
    
    for item in results:
        cat = item["category"]
        if cat in categories:
            sums[cat] += item["score"]
            amounts[cat] += 1
            
    bar_values = []
    for cat in categories:
        if amounts[cat] > 0:
            bar_values.append(round(sums[cat] / amounts[cat], 1))
        else:
            bar_values.append(0.0)

    plt.figure(figsize=(14, 6))
    plt.suptitle('Аналитика отзывов о ресторане', fontsize=16, fontweight='bold')

    plt.subplot(1, 2, 1)
    plt.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%')
    plt.title('Доля каждой оценки')

    plt.subplot(1, 2, 2)
    plt.bar(categories, bar_values, color=['blue', 'orange', 'green', 'red'])
    plt.title('Средняя оценка по критериям')
    plt.ylabel('Баллы')
    plt.ylim(0, 10)

    plt.tight_layout()
    plt.show()

def main():
    print("Запуск анализа отзывов...")
    logging.info("ЗАПУСК ПРОГРАММЫ")
    
    api_key = get_api_key("config.txt")
    if not api_key:
        print("Ошибка: не удалось загрузить API-ключ. Проверьте main_logs.log")
        return

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
    
    reviews = load_reviews("reviews.csv")
    if not reviews:
        print("Ошибка: файл данных пуст или не найден. Проверьте main_logs.log")
        return
        
    results = []
    active_reviews = reviews[:10]
    
    print(f"Обработка данных...")
    
    for index, text in enumerate(active_reviews, 1):
        score, category = analyze_review(client, text, index)
        results.append({"score": score, "category": category})

    logging.info("ЗАВЕРШЕНИЕ РАБОТЫ ПРОГРАММЫ")
    draw_dashboard(results)

if __name__ == "__main__":
    main()