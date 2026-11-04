# Деплой и индексация: чек-лист

## GitHub Pages

1. Settings → Pages → Source: ветка (`main`) и папка (`/` или `/docs`).
2. Домен: файл `CNAME` в корне публикуемой папки, ровно один домен, без `https://` и слэша.
3. После сохранения домена включить `Enforce HTTPS` (сертификат выпускается до ~24 ч).
4. Проверить `https://<domain>/` и `https://<domain>/index.html`; оба должны отдавать 200.

## DNS

| Запись | Имя | Значение |
| --- | --- | --- |
| A | @ | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 |
| CNAME | www | `<user>.github.io` |

- Apex-домен — только A/AAAA (CNAME на apex нельзя).
- `www` — CNAME на `github.io`, затем в Pages выбрать канонический вариант.
- Проверка: `nslookup <domain>`, `curl -I https://<domain>`.

## Верификация поисковиков

- Яндекс: скачать `yandex_<hash>.html`, положить в корень сайта, задеплоить, затем «Подтвердить». Файл должен открываться по `https://<domain>/yandex_<hash>.html`.
- Google Search Console: тот же приём с `google<hash>.html`, либо DNS-TXT.
- После подтверждения — отправить `sitemap.xml` вручную в обоих кабинетах; индексация не мгновенная.

## Минимум для индексируемости

```html
<link rel="canonical" href="https://example.ru/">
<meta property="og:title" content="...">
<meta property="og:image" content="https://example.ru/assets/og.jpg">
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.ru/</loc><changefreq>monthly</changefreq></url>
</urlset>
```

## Типовые провалы

- Домен привязан, но `CNAME` остался от старого сайта → 404 на Pages.
- Опечатка в телефоне/почте после редизайна → сверить с источником заказчика.
- Сайт открывается, но ассеты 404 из-за абсолютных путей `/assets/...` в подпапке репозитория.
- Кэш: проверять прод в приватном окне, иначе видно старую версию.
