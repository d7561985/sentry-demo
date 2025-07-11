# Sentry POC - iGaming Platform

Демонстрация возможностей Sentry для мониторинга распределенной системы iGaming платформы.

## 🚀 Подготовка к запуску

### 1. Настройка Sentry

1. **Создайте аккаунт в Sentry** (если еще нет):
   - Перейдите на https://sentry.io
   - Зарегистрируйтесь или войдите

2. **Создайте проекты в Sentry**:
   - В Sentry Dashboard нажмите "Create Project"
   - Создайте 7 проектов (по одному для каждого сервиса):
     - `igaming-frontend` (Platform: Browser/JavaScript)
     - `igaming-gateway` (Platform: Go)
     - `igaming-user` (Platform: Go)
     - `igaming-game` (Platform: Python)
     - `igaming-payment` (Platform: Node.js)
     - `igaming-analytics` (Platform: Python)
     - `igaming-wager` (Platform: PHP)

3. **Получите DSN для каждого проекта**:
   - Откройте каждый проект
   - Перейдите в Settings → Client Keys (DSN)
   - Скопируйте DSN (формат: `https://xxxxx@o123456.ingest.sentry.io/1234567`)

4. **Создайте Auth Token для загрузки Source Maps** (только для Frontend):
   - Перейдите на https://sentry.io/settings/account/api/auth-tokens/
   - Нажмите "Create New Token"
   - Назовите токен (например, "Source Maps Upload")
   - Выберите права доступа (ОБЯЗАТЕЛЬНО все три!):
     - `org:read` - для чтения информации об организации
     - `project:read` - для чтения информации о проекте
     - `project:write` - для загрузки source maps
     - `project:releases` - для создания релизов
   - Сохраните токен для использования в .env файле

5. **Настройте окружение**:
   
   **Основной .env файл (обязательно)**:
   ```bash
   cp .env.example .env
   ```
   
   Откройте `.env` и замените плейсхолдеры на реальные DSN:
   ```
   SENTRY_FRONTEND_DSN=https://YOUR_KEY@o123456.ingest.sentry.io/1234567
   SENTRY_GATEWAY_DSN=https://YOUR_KEY@o123456.ingest.sentry.io/1234568
   SENTRY_USER_DSN=https://YOUR_KEY@o123456.ingest.sentry.io/1234569
   SENTRY_GAME_DSN=https://YOUR_KEY@o123456.ingest.sentry.io/1234570
   SENTRY_PAYMENT_DSN=https://YOUR_KEY@o123456.ingest.sentry.io/1234571
   SENTRY_ANALYTICS_DSN=https://YOUR_KEY@o123456.ingest.sentry.io/1234572
   SENTRY_WAGER_DSN=https://YOUR_KEY@o123456.ingest.sentry.io/1234573
   ```
   
   **Frontend .env файл (для source maps)**:
   ```bash
   cd services/frontend
   cp .env.example .env
   ```
   
   Откройте `services/frontend/.env` и добавьте:
   ```
   SENTRY_ORG=your-org-slug
   SENTRY_PROJECT=your-project-slug
   SENTRY_AUTH_TOKEN=your-auth-token
   ```
   
   **Wager Service .env файл**:
   ```bash
   cd services/wager-service
   cp .env.example .env
   ```
   
   Откройте `services/wager-service/.env` и настройте:
   - `APP_SECRET` - сгенерируйте новый ключ для production
   - `SENTRY_DSN` - укажите DSN из проекта igaming-wager
   - Остальные параметры можно оставить по умолчанию для локальной разработки
   
   **Проверка конфигурации**:
   ```bash
   ./check-env.sh
   ```

### 2. Проверка портов

⚠️ **Важно**: Перед запуском убедитесь, что следующие порты свободны:
- **27017** - MongoDB
- **6379** - Redis  
- **5672, 15672** - RabbitMQ
- **8080-8086** - Микросервисы
- **4200** - Frontend

Если порты заняты:
```bash
# Проверить занятые порты
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "27017|6379|5672|8080"

# Остановить конфликтующие контейнеры
docker stop <container-name>
```

### 3. Запуск сервисов

#### Production Mode (с оптимизацией и загрузкой source maps)
```bash
# Запустите все сервисы в production режиме
# Source maps будут автоматически загружены в Sentry
./start-prod.sh

# Или базовый запуск без загрузки source maps
./start.sh
```

#### Development Mode (с отладкой, без загрузки source maps)
```bash
# Запустите в dev режиме с hot reload
./start-dev.sh

# Или вручную
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Различия между режимами**:
- **Production**: Оптимизированная сборка, source maps с debug-ids загружаются в Sentry
- **Development**: Hot reload, полная отладка, debug логи включены, source maps НЕ загружаются

### 🏷️ Версионирование и релизы

**Автоматическое версионирование**:
- Версия проекта хранится в файле `.version`
- При запуске `./start-prod.sh` версия автоматически инкрементируется
- Версия используется для:
  - Маркировки билдов в environment файлах
  - Создания релизов в Sentry
  - Ассоциации source maps с конкретным релизом
  - Отслеживания регрессий между версиями

**Debug IDs и Source Maps**:
- Debug IDs автоматически инжектируются при сборке Docker образа
- Source maps загружаются из развернутого контейнера (гарантия совпадения)
- Процесс полностью автоматизирован в `./start-prod.sh`
- Debug IDs обеспечивают 100% точность маппинга минифицированного кода

**Sentry релизы**:
- Автоматически создаются при production сборке
- Source maps привязываются к конкретному релизу и Debug IDs
- В Sentry Dashboard можно видеть:
  - Какие ошибки появились в новом релизе
  - Точный исходный код с номерами строк
  - Сравнение производительности между релизами

Дождитесь запуска всех сервисов (около 30 секунд).

## 📊 Scenario 1: Distributed Tracing Demo

### Цель демонстрации
Показать как Sentry отслеживает запросы через всю распределенную систему, выявляет узкие места и помогает быстро находить проблемы.

### Пошаговая инструкция

#### 1. Запустите демо
1. Откройте браузер: http://localhost:4200
2. Вы увидите простой интерфейс слот-машины с балансом $1000

#### 2. Выполните несколько спинов
1. Нажмите кнопку **SPIN ($10)** 5-10 раз
2. Обратите внимание: некоторые спины будут заканчиваться ошибкой (это нормально - 10% ошибок встроено специально)

#### 3. Откройте Sentry Dashboard
1. Перейдите в https://sentry.io
2. Откройте организацию и проект `igaming-frontend`

#### 4. Изучите Performance раздел
1. В левом меню выберите **Performance**
2. Найдите транзакцию `slot-machine-spin`
3. Кликните на неё для просмотра деталей

### 🔍 Что показывать и рассказывать

#### A. Полный Distributed Trace
**Где смотреть**: Performance → Transaction Details → Trace View

**Что рассказать**:
- "Видим полный путь запроса через 5 микросервисов"
- "Каждый сервис добавляет свой span в общий trace"
- "Можем точно видеть, где тратится время"

**Ключевые метрики**:
- Общее время выполнения: ~3-6 секунд
- Основная задержка: Payment Service (2-5 сек)

#### B. Проблемы производительности

**1. Медленный запрос в User Service**
- **Где**: Span `db.query` "Find user by ID"
- **Длительность**: 500ms+
- **Рассказать**: "Видим медленный запрос к MongoDB - отсутствует индекс. В реальной системе это было бы критично при высокой нагрузке"

**2. CPU Spike в Game Engine**
- **Где**: Span `game.rng` "Calculate slot result"
- **Длительность**: Варьируется
- **Рассказать**: "Неэффективный алгоритм расчета RNG создает нагрузку на CPU. Sentry помогает выявить такие проблемы"

**3. Медленный внешний API в Payment Service**
- **Где**: Span `http.client` "External payment provider API"
- **Длительность**: 2-5 секунд
- **Рассказать**: "Интеграция с платежным провайдером - самое узкое место. Нужно либо оптимизировать, либо сделать асинхронной"

#### C. Обработка ошибок

**Если попалась ошибка платежа**:
1. Перейдите в **Issues** в Sentry
2. Найдите "Payment provider timeout"
3. **Покажите**:
   - Stack trace с точным местом ошибки
   - User context (ID пользователя)
   - Связь с конкретным trace
   - Частоту возникновения (должно быть ~10%)

#### D. Custom метрики

**Где смотреть**: В деталях транзакции, секция Measurements

**Показать**:
- `game.bet_amount` - размер ставки
- `game.payout` - выигрыш (если был)
- `payment.processing_time` - время обработки платежа

**Рассказать**: "Можем отслеживать бизнес-метрики прямо в контексте производительности"

### 💡 Ключевые выводы для демо

1. **MTTR (Mean Time To Resolution)**:
   - "Без Sentry: поиск проблемы в 5 сервисах занял бы часы"
   - "С Sentry: видим проблему за секунды"

2. **Производительность**:
   - "Сразу видны все bottlenecks"
   - "Можем приоритизировать оптимизации"

3. **Бизнес-impact**:
   - "10% ошибок платежей = прямая потеря revenue"
   - "Медленный отклик = потеря игроков"

### 🎯 Дополнительные демо

#### N+1 Query Problem (опционально)
Если хотите показать N+1 проблему:
1. В браузере добавьте к URL: `?include_history=true`
2. Сделайте спин
3. В Sentry увидите множество span'ов `db.query.game`
4. Объясните проблему неэффективных запросов

#### Panic в Go сервисе
Для демо обработки паник:
```bash
curl http://localhost:8080/api/v1/debug/panic/panic-test
```
Покажет как Sentry ловит панику в Go.

### 🎥 Session Replay (Новая функция!)

#### Что показывать
1. **При любой ошибке** в Sentry теперь доступен Session Replay
2. В деталях ошибки найдите вкладку **Replay**
3. Покажите:
   - Полную запись действий пользователя до ошибки
   - Клики, ввод текста, навигацию
   - Сетевые запросы с таймингами
   - Console logs и ошибки
   - DOM изменения

#### Ключевые преимущества
- **Воспроизведение проблемы**: Видите точно, что делал пользователь
- **Контекст ошибки**: Понимаете, как пользователь пришел к ошибке
- **Отладка UX**: Видите проблемы с интерфейсом
- **Privacy-friendly**: Можно маскировать чувствительные данные

#### Демо Session Replay
1. Откройте Debug Panel
2. Сделайте несколько спинов
3. Вызовите любую ошибку через Debug Panel
4. В Sentry откройте эту ошибку → вкладка Replay
5. Покажите видео сессии пользователя

## 🚀 Scenario 3: Performance Monitoring

Демонстрация возможностей Sentry по выявлению проблем производительности.

### Реализованные проблемы:
- **N+1 Query Problem** в User Service
- **CPU Spike** с генерацией простых чисел в Game Engine  
- **Slow MongoDB Aggregation** в Analytics Service
- **External API Latency** в Payment Service

### Быстрый старт:
1. Откройте Debug Panel в интерфейсе
2. Найдите секцию "Performance Issues"
3. Нажимайте кнопки для воспроизведения проблем
4. Смотрите результаты в Sentry Performance

**Подробная инструкция**: [docs/scenario-3-performance-demo.md](docs/scenario-3-performance-demo.md)

## 🆕 Новые возможности в POC

### Wager Service (PHP/Symfony)
- **Технологии**: PHP 8.1+, Symfony 5.4 LTS, MongoDB с Doctrine ODM
- **Sentry демо**: Медленные aggregations, валидация бонусов, бизнес-метрики
- **Порт**: 8086 (Swagger UI: http://localhost:8086/api/doc)

### Улучшенная обработка ошибок
- Детальные crash демонстрации для всех сервисов
- Panic recovery в Go сервисах
- Structured logging с контекстом

### Debug панель в Frontend
- Быстрый доступ ко всем демо-сценариям
- Триггеры для различных типов ошибок
- Performance проблемы по кнопке

## 📨 RabbitMQ Analytics Integration

Демонстрация distributed tracing через асинхронные очереди сообщений.

### Архитектура
- **Publishers**: Game Engine и Payment Service публикуют события
- **Message Queue**: RabbitMQ с exchange "gaming"
- **Consumer**: Analytics Service обрабатывает сообщения в реальном времени
- **Трассировка**: Полный trace от HTTP запроса через MQ до обработки

### Ключевые возможности:
- ✅ Trace propagation через RabbitMQ
- ✅ Real-time analytics с предагрегацией
- ✅ Resilience: система работает даже если аналитика недоступна
- ✅ Автоматическое восстановление при сбоях

### Доступ к RabbitMQ Management:
- URL: http://localhost:15672
- Login: admin / password

**Подробная инструкция**: [docs/rabbitmq-analytics-demo.md](docs/rabbitmq-analytics-demo.md)

## 🛠 Troubleshooting

**Сервисы не запускаются**:
```bash
docker-compose logs -f [service-name]
```

**Нет данных в Sentry**:
- Проверьте DSN в `.env`
- Убедитесь что все 6 проектов созданы
- Проверьте `tracesSampleRate: 1.0` в коде

**Неполные traces**:
- Подождите 1-2 минуты после спина
- Обновите страницу в Sentry
- Проверьте что все сервисы запущены: `docker-compose ps`

## 🏭 Production Recommendations / Рекомендации для продакшена

### Source Maps Configuration

**Что настроено**:
- ✅ Source maps генерируются при production сборке
- ✅ Release tracking для связи ошибок с версиями
- ✅ Правильная конфигурация для Sentry SDK v7

**Что нужно сделать для продакшена**:
1. Загружать source maps в Sentry при каждом деплое
2. Удалять source maps с публичного сервера после загрузки
3. Использовать Sentry CLI или webpack plugin для автоматизации

**Детали**: См. [services/frontend/SENTRY_SOURCEMAPS.md](services/frontend/SENTRY_SOURCEMAPS.md)

### Performance Considerations / Влияние на производительность

#### Frontend (Angular)
- **Source Maps**: 
  - Влияние на сборку: +10-20% времени
  - Влияние на размер: 0% (отдельные файлы)
  - Runtime влияние: 0% (загружаются только с DevTools)
- **Sentry SDK**:
  - Размер: ~70KB gzipped
  - CPU: Минимальное (< 1%)
  - Сеть: ~1KB на транзакцию

#### Backend Services
- **Go Services**: 
  - CPU overhead: < 0.5%
  - Memory: ~10MB на сервис
  - Latency: < 1ms на запрос
- **Python/Node.js**:
  - CPU overhead: < 1%
  - Memory: ~20-30MB
  - Latency: < 2ms на запрос

### Security Recommendations / Безопасность

1. **Source Maps**:
   ```json
   // Для production используйте hidden source maps
   "sourceMap": {
     "scripts": true,
     "hidden": true,
     "vendor": false
   }
   ```

2. **Sensitive Data**:
   - Используйте `beforeSend` для фильтрации
   - Не логируйте пароли, токены, личные данные
   - Настройте Data Scrubbing в Sentry

3. **DSN Protection**:
   - Используйте разные DSN для dev/prod
   - Ограничьте домены в настройках проекта
   - Включите rate limiting

### Optimization Tips / Оптимизации

1. **Sampling для высоких нагрузок**:
   ```javascript
   // Вместо 100% трейсинга
   tracesSampleRate: 0.1, // 10% в продакшене
   
   // Или динамический sampling
   tracesSampler: (samplingContext) => {
     // Важные транзакции - 100%
     if (samplingContext.transactionContext.name === 'payment') {
       return 1.0;
     }
     // Остальные - 10%
     return 0.1;
   }
   ```

2. **Профилирование** (осторожно в проде):
   ```javascript
   profilesSampleRate: 0.01, // 1% для production
   ```

3. **Уменьшение данных**:
   - Отключите debug mode
   - Используйте `ignoreErrors` для известных ошибок
   - Настройте `maxBreadcrumbs` (по умолчанию 100)

### Monitoring Best Practices

1. **Alerts Configuration**:
   - Error rate > 1% → Critical
   - P95 latency > 1s → Warning  
   - Failed payments > 5% → Critical

2. **Dashboards**:
   - Создайте отдельные дашборды для:
     - Business metrics (RTP, активные сессии)
     - Technical metrics (latency, errors)
     - Payment success rate

3. **Release Process**:
   - Всегда указывайте release версию
   - Используйте semantic versioning
   - Настройте release health tracking

### Cost Management / Управление стоимостью

- **Transactions**: Основной драйвер стоимости
- **Рекомендации**:
  - Используйте sampling в production
  - Настройте фильтры для health checks
  - Регулярно чистите старые данные
  - Мониторьте usage в Sentry

### Example Production Config

```javascript
// Frontend (main.ts)
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  release: process.env.RELEASE_VERSION,
  environment: 'production',
  tracesSampleRate: 0.1,
  profilesSampleRate: 0.01,
  // Session Replay для production
  replaysSessionSampleRate: 0.01, // 1% обычных сессий
  replaysOnErrorSampleRate: 1.0,   // 100% сессий с ошибками
  integrations: [
    new Sentry.Replay({
      // Privacy settings для production
      maskAllText: true,     // Маскировать весь текст
      maskAllInputs: true,   // Маскировать все input
      blockAllMedia: true,   // Блокировать media
      // Маскировать специфичные селекторы
      mask: ['.sensitive', '.credit-card', '.password'],
      // Исключения для маскировки
      unmask: ['.game-result', '.balance'],
      // Ограничить сетевые детали
      networkDetailAllowUrls: [window.location.origin],
      networkRequestHeaders: ['X-Request-ID'],
      networkResponseHeaders: ['X-Response-ID'],
    }),
  ],
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection captured'
  ],
  beforeSend(event, hint) {
    // Фильтрация sensitive данных
    if (event.request?.cookies) {
      delete event.request.cookies;
    }
    return event;
  }
});
```

### Session Replay Privacy Настройки

Для iGaming важно правильно настроить приватность:

```javascript
// Маскировка для production
const replayConfig = {
  // Базовые настройки
  maskAllText: true,        // Скрыть весь текст
  maskAllInputs: true,      // Скрыть все вводы
  blockAllMedia: true,      // Блокировать медиа
  
  // Специфичные для iGaming
  mask: [
    '[data-sensitive]',     // Пользовательские данные
    '.user-balance',        // Баланс (если нужно скрыть)
    '.payment-info',        // Платежная информация
    'input[type="password"]', // Пароли
  ],
  
  // Что можно показывать
  unmask: [
    '.game-board',          // Игровое поле
    '.spin-result',         // Результаты игры
    '.error-message',       // Сообщения об ошибках
  ],
  
  // Sampling
  sessionSampleRate: 0.01,  // 1% всех сессий
  errorSampleRate: 1.0,     // 100% сессий с ошибками
};
```


## 📋 Environment Variables Reference

### Root .env файл

| Variable | Description | Example |
|----------|-------------|---------|
| `SENTRY_FRONTEND_DSN` | DSN для Frontend проекта | `https://xxx@o123456.ingest.sentry.io/1234567` |
| `SENTRY_GATEWAY_DSN` | DSN для API Gateway | `https://xxx@o123456.ingest.sentry.io/1234568` |
| `SENTRY_USER_DSN` | DSN для User Service | `https://xxx@o123456.ingest.sentry.io/1234569` |
| `SENTRY_GAME_DSN` | DSN для Game Engine | `https://xxx@o123456.ingest.sentry.io/1234570` |
| `SENTRY_PAYMENT_DSN` | DSN для Payment Service | `https://xxx@o123456.ingest.sentry.io/1234571` |
| `SENTRY_ANALYTICS_DSN` | DSN для Analytics Service | `https://xxx@o123456.ingest.sentry.io/1234572` |
| `SENTRY_WAGER_DSN` | DSN для Wager Service | `https://xxx@o123456.ingest.sentry.io/1234573` |
| `SENTRY_TRACES_SAMPLE_RATE` | Процент трейсов для отправки | `1.0` (100% для dev, `0.1` для prod) |
| `SENTRY_AUTH_TOKEN` | Токен для Sentry CLI операций | Получить на sentry.io |
| `API_URL` | URL API Gateway | `http://localhost:8080` |
| `APP_VERSION` | Версия приложения | `1.0.0` |

### Frontend .env файл

| Variable | Description | Example |
|----------|-------------|---------|
| `SENTRY_ORG` | Slug вашей организации в Sentry | `my-company` |
| `SENTRY_PROJECT` | Slug проекта в Sentry | `igaming-frontend` |
| `SENTRY_AUTH_TOKEN` | Токен для загрузки source maps | См. инструкцию выше |

### Wager Service .env файл

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_ENV` | Окружение Symfony | `dev`, `test`, `prod` |
| `APP_SECRET` | Секретный ключ Symfony | Сгенерировать новый для prod |
| `MONGODB_URL` | Строка подключения к MongoDB | `mongodb://admin:password@mongodb:27017/sentry_poc?authSource=admin` |
| `MONGODB_DB` | Имя базы данных | `sentry_poc` |
| `SENTRY_DSN` | DSN для Sentry | Взять из проекта igaming-wager |
| `USER_SERVICE_URL` | URL User Service | `http://user-service:8081` |
| `PAYMENT_SERVICE_URL` | URL Payment Service | `http://payment-service:8083` |
| `APP_VERSION` | Версия сервиса | `1.0.0` |

### Генерация секретов

**Symfony APP_SECRET**:
```bash
# Вариант 1: PHP
php -r "echo bin2hex(random_bytes(16));"

# Вариант 2: OpenSSL
openssl rand -hex 16

# Вариант 3: Symfony console (если установлен)
php bin/console secrets:generate-keys
```

### Проверка конфигурации

После настройки всех .env файлов, проверьте корректность:
```bash
# Проверка основных переменных
./check-env.sh

# Проверка Sentry DSN (должны быть все 7 проектов)
grep SENTRY_.*_DSN .env | wc -l  # Должно вернуть 7

# Проверка что DSN не пустые
grep SENTRY_.*_DSN .env | grep -v "="$  # Не должно быть вывода
```

# ToDo

* мне не нравится что каждый клик на фронте трейст создает это нужно оптимизировать!
* как работают аномалии