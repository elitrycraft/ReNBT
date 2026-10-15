#!/usr/bin/env python3
"""Генерация release notes через OpenDeep на основе коммитов и файлов репозитория."""
import os
import sys
import pathlib

TOKEN = os.environ.get("DEEPSEEK_TOKEN")
VERSION = os.environ.get("VERSION", "dev")

if not TOKEN:
    print("::error::DEEPSEEK_TOKEN не задан")
    sys.exit(1)

commits_file = pathlib.Path("commits.txt")
files_file = pathlib.Path("files.txt")
output_file = pathlib.Path("release_notes.md")

commits = commits_file.read_text(encoding="utf-8") if commits_file.exists() else "(нет коммитов)"
files_info = files_file.read_text(encoding="utf-8") if files_file.exists() else "(нет данных о файлах)"

# Ограничим размер, чтобы не переполнить контекст
files_info = files_info[:8000]

prompt = f"""Ты — технический писатель, который ведёт changelog для open-source проекта ReNBT.
Версия релиза: {VERSION}.

Составь описание релиза на **двух языках** — сначала русский, затем английский.
Используй красивое Markdown-форматирование: заголовки, эмодзи, списки, `code` для имён файлов и функций,
**жирный** для ключевых изменений. Без вступлений вроде «Вот описание релиза» — только сам текст.

Опирайся ТОЛЬКО на:
1. Список последних коммитов (главный источник правды).
2. Структуру репозитория и содержимое ключевых файлов (только для контекста — не описывай то,
   что не менялось).

Правила:
- Игнорируй всё, что относится к `.github/`, CI, служебным и временным файлам.
- Пиши только о недавних изменениях, не пересказывай весь проект.
- Не выдумывай функции, которых нет в коммитах.
- Если раздел пустой — не включай его вовсе.
- Группируй изменения по смыслу, а не по одному пункту на коммит.
- Для каждого пункта — короткое пояснение «что это даёт пользователю», если это уместно.

Структура ответа строго такая:

# 🇷🇺 Русский

## ✨ Новое
- ...

## 🐛 Исправления
- ...

## 🔧 Изменения
- ...

# 🇬🇧 English

## ✨ Added
- ...

## 🐛 Fixed
- ...

## 🔧 Changed
- ...

---

=== ПОСЛЕДНИЕ КОММИТЫ ===
{commits}

=== ФАЙЛЫ РЕПОЗИТОРИЯ ===
{files_info}
"""

try:
    import opendeep
    from opendeep import GenerativeModel

    opendeep.configure(api_key=TOKEN)
    model = GenerativeModel("deepseek-v4-pro")
    response = model.generate_content(prompt, thinking_enabled=False)
    notes = (response.text or "").strip()
except Exception as e:
    print(f"::warning::DeepSeek не ответил: {e}")
    notes = f"Релиз {VERSION}. Автоматическое описание недоступно."

if not notes:
    notes = f"Релиз {VERSION}."

output_file.write_text(notes, encoding="utf-8")
print("=== Release notes сгенерированы ===")
print(notes)
