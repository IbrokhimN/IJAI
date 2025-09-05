import wikipediaapi
import time
import random
import os

wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent="IJAI-LearningBot/1.0 (contact: ibragim@example.com)"
)

start_pages = ["Science", "Technology", "Art", "History", "Culture", "Sports", "Geography"]

articles = set()
MAX_ARTICLES = 100000
PAUSE = 0.5  # пауза между запросами

def collect_articles_from_page(page, depth=0, max_depth=3):
    """Собираем статьи с главной страницы и её ссылок случайно"""
    if len(articles) >= MAX_ARTICLES or depth > max_depth:
        return

    links = list(page.links.values())
    random.shuffle(links)  # случайный порядок для разнообразия
    for link in links:
        if len(articles) >= MAX_ARTICLES:
            break
        title = link.title
        if title.startswith(("Category:", "File:", "Template:")):
            continue
        if title not in articles:
            articles.add(title)
            print(f"✅ Добавлена статья {len(articles)}: {title}")
            time.sleep(PAUSE)
        # рекурсивно переходим на страницу ссылки
        collect_articles_from_page(link, depth + 1, max_depth)

# Собираем статьи
for sp in start_pages:
    page = wiki.page(sp)
    collect_articles_from_page(page)

# Сохраняем в файл
os.makedirs("dataset", exist_ok=True)
with open("articles.txt", "w", encoding="utf-8") as f:
    for a in sorted(articles):
        f.write(a + "\n")

print(f"🎉 articles.txt создан с {len(articles)} реальными темами из Википедии")

