# Source Maps Setup для Sentry v7

## Проблема
Sentry не видит source maps в dev режиме, потому что:
1. В dev режиме source maps генерируются inline
2. Sentry v7 требует загрузки source maps на сервер Sentry

## Решение для Development

### Вариант 1: Локальные source maps (рекомендуется для dev)

1. Убедитесь, что запущен dev режим:
```bash
./start-dev.sh
```

2. В браузере откройте DevTools (F12)
3. Source maps будут работать локально в браузере
4. В Sentry будут видны минифицированные стеки, но с правильными именами файлов

### Вариант 2: Загрузка source maps в Sentry

1. Получите auth token:
   - Зайдите в https://sentry.io/settings/account/api/auth-tokens/
   - Создайте новый токен с правами: `project:releases`
   - Скопируйте токен

2. Установите переменные окружения:
```bash
export SENTRY_AUTH_TOKEN=your-token-here
export SENTRY_ORG=ggr-oi
export SENTRY_PROJECT=igaming-frontend
```

3. Соберите приложение и загрузите source maps:
```bash
cd services/frontend
npm run build:dev
./upload-sourcemaps.sh 1.0.0-dev
```

4. Перезапустите frontend контейнер:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart frontend
```

## Решение для Production

Для production автоматически загружайте source maps в CI/CD:

```yaml
# GitHub Actions пример
- name: Build and Upload Source Maps
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
  run: |
    npm run build:prod
```

## Проверка работы source maps

1. Вызовите ошибку через debug panel
2. Откройте Sentry dashboard
3. Найдите ошибку
4. Проверьте stack trace - должен показывать оригинальный код

## Troubleshooting

### "Source code was not found"
- Проверьте, что release версия совпадает в коде и при загрузке
- Убедитесь, что URL prefix правильный (должен быть `~/`)

### Stack trace все еще минифицирован
- Проверьте, что source maps действительно загружены:
  ```bash
  npx @sentry/cli releases files 1.0.0-dev list
  ```
- Убедитесь, что в Sentry правильный release

### Ошибка аутентификации
- Проверьте SENTRY_AUTH_TOKEN
- Убедитесь, что токен имеет права `project:releases`
- Проверьте org и project в .sentryclirc

## Важно для нашей версии

- У нас Sentry SDK v7, НЕ v8
- Angular 13, НЕ последняя версия
- Node 14, НЕ последняя версия

Не используйте команды для новых версий!