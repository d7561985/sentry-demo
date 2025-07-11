# Тестирование интеграции логирования Sentry

## Что было реализовано:

1. **captureConsoleIntegration** - перехватывает ВСЕ уровни console.* вызовов:
   - console.log
   - console.info
   - console.debug
   - console.warn
   - console.error
   - console.trace

2. **Экспериментальная поддержка логов** - включена через `_experiments: { enableLogs: true }`

3. **Кнопка "Demo Console Logs"** в Debug Panel, которая демонстрирует:
   - Различные уровни логирования
   - Структурированные данные в логах
   - Sentry breadcrumbs
   - Custom context и tags

## Как протестировать:

1. Запустите фронтенд:
   ```bash
   cd services/frontend
   npm start
   ```

2. Откройте http://localhost:4200

3. Нажмите "Show Debug Panel"

4. В секции "Frontend Errors" нажмите "📝 Demo Console Logs"

5. В Sentry Dashboard вы увидите:
   - Все console.* вызовы в breadcrumbs
   - Структурированные данные с каждым логом
   - Custom context с состоянием игры
   - Tags для фильтрации

## Что происходит при каждом спине:

- Автоматически логируется результат спина через console.log
- Данные структурированы (win, payout, symbols, newBalance)
- Все логи попадают в Sentry как breadcrumbs

## Дополнительные возможности:

- **Sentry.addBreadcrumb()** - для добавления custom breadcrumbs
- **Sentry.setContext()** - для добавления контекста
- **Sentry.setTags()** - для тегирования событий