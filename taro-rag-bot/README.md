# Knowledge Base: The Paths (вымышленный мир)

## Что это

База знаний для RAG-бота, построенная на основе системы Таро.
Все ключевые термины заменены на вымышленные, чтобы LLM не могла
ответить по памяти и была вынуждена обращаться к векторному индексу.

## Источник

Wikipedia (CC BY-SA 4.0). Спарсено скриптом `scripts/parser.py`,
сохранено в `raw_docs/`, затем переработано `scripts/replacer.py`.

## Логика замены

Система Таро → «The Paths»:
- Старшие Арканы → Greater Paths (22 документа)
- Младшие Арканы → Lesser Paths (4 масти)
- Стихии → Elements (4 документа)

Словарь замен — `terms_map.json` (исходное → вымышленное).

## Структура

- `greater_paths/` — 22 карты (The Wanderer, The Weaver, ...)
- `lesser_paths/` — 4 масти (Ember Staves, Tide Vessels, ...)
- `elements/` — 4 стихии (Fire, Water, Air, Earth)
- `terms_map.json` — словарь замен

## Проверка

`scripts/check_terms.py` ищет остаточные термины Таро.
Цель — 0 совпадений.
