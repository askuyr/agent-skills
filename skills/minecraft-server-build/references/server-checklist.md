# Сервер: команды и конфиги

## Стартовый скрипт (Paper)

```bat
@echo off
cd /d C:\mcserver
java -Xms2G -Xmx6G -XX:+UseG1GC -jar paper.jar nogui
pause
```

## Стартовый скрипт (Fabric)

```bat
@echo off
cd /d C:\mcserver
java -Xms2G -Xmx6G -jar fabric-server-launch.jar nogui
pause
```

## Ключевые строки `server.properties`

```properties
white-list=false
online-mode=true
max-players=8
view-distance=8
simulation-distance=6
server-port=25565
```

## Импорт мира из архива

1. Распаковать в `C:\mcserver\_import_world`.
2. Найти `level.dat`:
   - в корне распаковки → корень мира = папка распаковки;
   - внутри `world\level.dat` → корень мира = `world`.
3. Бэкап:
   ```powershell
   $stamp = Get-Date -Format yyyy-MM-dd
   robocopy C:\mcserver\world "C:\mcserver\backup\world_old_$stamp" /E
   ```
   `%DATE%` не использовать: в русской локали даёт точки, в других — слэши и невалидное имя папки.
4. Скопировать корень мира в `C:\mcserver\<WorldName>`, прописать `level-name=<WorldName>`.

## Modrinth `.mrpack`

- `.mrpack` — zip: `modrinth.index.json` (список модов) + `overrides/` (конфиги, ресурспаки).
- Для сервера: моды из индекса скачать по `downloads[0]`, положить в `mods/`; `overrides/` наложить поверх.
- Клиентская часть — тот же архив друзьям (или установщик Modrinth), версия и лоадер должны совпадать.

## Radmin VPN

- Создать/подключиться к сети, взять IPv4 вида `26.x.x.x` у хоста.
- Друзьям: адрес `26.x.x.x:25565`, Radmin-сеть та же.
- Проверка на хосте: `netstat -ano | findstr 25565` — должен быть `0.0.0.0:25565`.
- Брандмауэр: правило на входящий TCP 25565 для `java.exe`.

## Диагностика

| Симптом | Причина |
| --- | --- |
| `UnsupportedClassVersionError` | старая Java |
| Друзья не видят сервер | Radmin не подключён / брандмауэр / неверный IP |
| Пропали инвентари | другой мир или смена версии; бэкап `world_old_*` |
| Пропали скины | `online-mode=false` или offline-аккаунты |
| Сервер падает на старте | конфликт модов, несовпадение лоадера, нехватка RAM |
