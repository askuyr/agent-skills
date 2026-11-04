---
name: unreal-engine
description: >-
  Использовать на «сделай игру на Unreal», «Unreal Engine 5», «UE5», «Blueprint»,
  «C++ в Unreal», «упакуй проект Unreal», «собери билд»: создать или починить
  проект UE5, выбрать Blueprint или C++, собрать и упаковать игру под Windows.
license: MIT
---

# Unreal Engine 5

Игра, а не технологическая демка. Сначала вертикальный срез на 5–10 минут, потом контент.

## Порядок

1. **Инвентаризация.** `.uproject` (поле `EngineAssociation`), `Source/`, `Content/`, `Config/DefaultEngine.ini`, установленные движки в `C:\Program Files\Epic Games\UE_5.*`. Версия проекта и движка должны совпадать; апгрейд — только после бэкапа.
2. **Новый проект.** Epic Games Launcher → Games → Blank (Blueprint или C++), Desktop, Starter Content только если реально нужен. Не собирать проект копированием чужих папок.
3. **Blueprint или C++.**
   - Blueprint: геймплей, UI, прототип, контентная логика. Быстро, но большие системы и массовые акторы тормозят.
   - C++: подсистемы, производительность, акторы с сотнями экземпляров, код для Git. `UCLASS`/`UPROPERTY`/`UFUNCTION(BlueprintCallable)`.
   - Новый `UCLASS` требует перезапуска редактора: Live Coding его не создаёт.
4. **Сборка C++.** Правый клик по `.uproject` → Generate Visual Studio project files, собрать `Development Editor`. Ошибки — в Output Log и `Saved/Logs/*.log`.
5. **Проверка.** PIE, `stat unit`, `stat fps`, `stat memory`. Логику — через Session Frontend → Automation или функциональные тесты.
6. **Упаковка.** Project Settings → Maps & Modes (default map) и Packaging → List of maps to include. Затем Platforms → Windows → Package Project, либо CLI:
   ```
   "<UE>\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun -project="<abs>\Game.uproject" -noP4 -platform=Win64 -clientconfig=Shipping -cook -build -stage -pak -archive -archivedirectory="<abs>\Build"
   ```
7. **Проверить билд** в чистой папке: запускается, карта грузится, сохранения пишутся в `Saved/`.

## Правила проекта

- Git + LFS для `*.uasset`, `*.umap`, `*.png`, `*.wav`. В `.gitignore`: `Binaries/`, `DerivedDataCache/`, `Intermediate/`, `Saved/`, `.vs/`.
- Ассеты только в `/Game/...`; префиксы `BP_`, `SM_`, `M_`, `T_`, `AN_`. Мусор из Content удалять.
- Настройки — в `Config/*.ini`, не в коде.
- Слабые ПК: выключить Lumen/Nanite, Forward Shading, запечённый свет, `r.ScreenPercentage`.
- Мобилки/консоли: сначала проверить ограничения рендера, потом делать контент.

## Лицензия

UE бесплатен до $1M lifetime gross на продукт, дальше 5% royalty. Условия менялись — сверять на unrealengine.com. Лицензию каждого ассета из Fab/Quixel проверять отдельно.

## Риски

- Апгрейд движка ломает Blueprint/C++ → бэкап и отдельная ветка.
- Карта не добавлена в Maps to Cook → чёрный экран или краш в билде.
- Live Coding не подхватывает новые классы и изменения `UCLASS` → перезапуск редактора.
- Пиратский UE и плагины сомнительного происхождения — не использовать.

## Чего не делать

- Не тащить плагины «на всякий случай».
- Не начинать с открытого мира, мультиплеера и сложной сети — сначала один законченный уровень.
