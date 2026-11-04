---
name: free-game-engines
description: >-
  Использовать на «бесплатный движок», «на чём сделать игру», «Godot», «Unity бесплатно»,
  «Defold», «2D игра», «мобильная игра без подписки»: выбрать бесплатный движок,
  собрать проект и экспортировать билд без платных лицензий.
license: MIT
---

# Бесплатные движки

## Выбор

| Задача | Движок | Почему |
|---|---|---|
| 2D, пиксель-арт, инди | Godot 4 | MIT, без роялти, лёгкий, экспорт в Windows/Linux/Web/Android |
| 3D инди, C# | Unity Personal | бесплатен до порога выручки; Runtime Fee отменён — сверять текущие условия |
| 2D мобилки/веб, малый вес | Defold | бесплатный, быстрый, Lua |
| обучение, GameMaker-подобное | GameMaker Free | бесплатная версия с ограничениями экспорта |

Не платить за движок, пока не упёрлись в его лимит. «Free» ≠ open source: читать лицензию.

## Godot 4 (по умолчанию)

1. Скачать standard (не .NET, если не нужен C#), распаковать, запустить.
2. Структура: `project.godot`, сцены `*.tscn`, скрипты `*.gd`, импорт в `res://`. Исходники — в `assets/`, не в корне.
3. Сцена — дерево Node. Сигналы вместо прямых ссылок, `@export` для настроек, `@onready` для ссылок.
4. Main scene: Project Settings → Application → Run → Main Scene.
5. Пиксель-арт: Rendering → Textures → Canvas Textures → Default Texture Filter = Nearest; Stretch Mode = `canvas_items`.
6. Сохранения: `FileAccess.open("user://save.json", ...)` + `JSON.stringify`; не писать в `res://`.
7. Запуск: `godot --path .`; быстрая проверка без окна: `godot --headless --path . --quit`.
8. Экспорт: установить Export Templates, Project → Export → Windows Desktop (`.exe` + `.pck`):
   ```
   godot --headless --path . --export-release "Windows Desktop" build/Game.exe
   ```
9. Тесты: GUT или `--headless` скрипт с `assert`; проверять загрузку главной сцены, сохранение, повторный запуск.

## Unity Personal

- Unity Hub → актуальный LTS → шаблон 2D (или 3D URP).
- Personal бесплатен до годовой выручки $200k; условия и сборы менялись — сверять с unity.com/pricing.
- Пакеты только по делу; `Packages/manifest.json` — источник зависимостей.

## Defold

- Бесплатный, лёгкий, Lua. Хорош для 2D-мобайла и веба. Сборка через редактор или `bob.jar`.

## Ассеты

- Бесплатные: Kenney (CC0), OpenGameArt (фильтр по лицензии), Freesound (проверять лицензию), Mixamo (анимации, условия Adobe).
- Музыка и шрифты — только с явной лицензией; CC-BY требует атрибуции.

## Риски

- Смена лицензии движка — не строить бизнес на «бесплатно навсегда».
- Godot .NET требует .NET SDK; Android-экспорт — JDK + Android SDK.
- Web-экспорт тяжёлый, мобилки требуют тестов на реальном устройстве.
- Пиратские ассеты и «free» паки без лицензии — не использовать.

## Чего не делать

- Не выбирать движок по хайпу: 2D на Unity/Unreal — лишний вес.
- Не начинать с открытого мира и мультиплеера — сначала 5–10 минут геймплея.
