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

prompt = f"""Ты — технический писатель. Составь краткое описание релиза на русском языке
для проекта ReNBT (версия {VERSION}).

Тебе даны:
1. Список последних коммитов
2. Структура репозитория и содержимое ключевых файлов

На их основе опиши:
- что нового добавлено,
- что исправлено,
- какие изменения в API/поведении/структуре.
- не обращай внимание на файлы в .github и служебных папках

Формат ответа (Markdown, без вступлений и лишних слов):

## ✨ Новое
- ...

## 🐛 Исправления
- ...

## 🔧 Изменения
- ...

Если какой-то раздел пустой — не включай его.

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
