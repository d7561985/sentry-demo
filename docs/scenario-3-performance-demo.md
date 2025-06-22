# Scenario 3: Performance Monitoring Demo Guide

## Обзор

Scenario 3 демонстрирует возможности Sentry по мониторингу производительности и выявлению узких мест в распределенной системе. 

### Реализованные проблемы производительности:

1. **N+1 Query Problem** (User Service)
2. **CPU Spike** (Game Engine) 
3. **Slow MongoDB Aggregation** (Analytics Service)
4. **External API Latency** (Payment Service - уже существует)

## 🚀 Запуск демо

### Подготовка

1. Убедитесь, что все сервисы запущены:
```bash
./start.sh
# или
docker-compose up -d
```

2. Откройте frontend: http://localhost:4200

3. Откройте Sentry Dashboard и перейдите в раздел **Performance**

### Использование Debug Panel

1. В интерфейсе слот-машины нажмите **"🐛 Show Debug Panel"**
2. Найдите секцию **"Performance Issues"**

## 📊 Демонстрация проблем производительности

### 1. N+1 Query Problem

**Что демонстрируем**: Неэффективный паттерн запросов к БД

**Как воспроизвести**:
1. В Debug Panel нажмите **"🐌 Trigger N+1 Query"**
2. Дождитесь завершения (5-10 секунд)

**Что показать в Sentry**:
1. Performance → найдите транзакцию `user.get_history`
2. Откройте Trace View
3. Покажите:
   - Span `db.query.history` с вложенными запросами
   - 20+ отдельных запросов `db.query.single_game`
   - Каждый запрос занимает 50ms+
   - Общее время: 1-2 секунды на 20 записей

**Ключевые моменты**:
- "Вместо 1 запроса - делаем 21 (1 для IDs + 20 для каждой игры)"
- "В production с тысячами игр это займет минуты"
- "Решение: использовать один запрос с $in оператором"

### 2. CPU Spike (Prime Number Generation)

**Что демонстрируем**: Неэффективные вычисления, нагружающие CPU

**Как воспроизвести**:
1. В Debug Panel нажмите **"🔥 Trigger CPU Spike"**
2. Ждите ~5-10 секунд

**Что показать в Sentry**:
1. Performance → найдите транзакцию `game.calculate`
2. Откройте детали транзакции
3. Покажите:
   - Span `cpu.prime_generation` (несколько секунд)
   - Span `cpu.heavy_calculation` с большим количеством итераций
   - Общее время выполнения 5-10 секунд

**Ключевые моменты**:
- "Генерация простых чисел начиная с 1,000,000"
- "30,000+ математических операций для RNG"
- "Блокирует event loop в Python"
- "В production это может привести к timeout"

### 3. Slow MongoDB Aggregation

**Что демонстрируем**: Неоптимизированные запросы aggregation

**Как воспроизвести**:
1. В Debug Panel нажмите **"📊 Trigger Slow Analytics"**
2. Ждите ~5-15 секунд

**Что показать в Sentry**:
1. Performance → найдите транзакцию `analytics.daily_stats`
2. Откройте Trace View
3. Покажите:
   - Span `db.aggregate` с тегом `performance.issue: missing_index`
   - Full collection scan на поле timestamp
   - 5 стадий aggregation pipeline
   - Дополнительные вычисления running totals

**Ключевые моменты**:
- "Нет индекса на поле timestamp"
- "Full collection scan для каждого запроса"
- "Сложный pipeline с $addFields и вычислениями"
- "Решение: compound index на (timestamp, user_id)"

### 4. Комбинированный сценарий

**Для полной демонстрации distributed tracing**:

1. Сделайте обычный спин (кнопка SPIN)
2. Затем вызовите N+1 query
3. Покажите в Sentry как все связано в одном trace

## 🎯 Ключевые метрики для демо

### Transaction Summary
- **p50**: <100ms (нормальные запросы)
- **p95**: >1s (с performance issues)
- **p99**: >5s (CPU spike scenarios)

### Database Queries
- N+1 pattern: 20+ queries вместо 1
- Missing indexes: full collection scans
- Query time: 50-500ms per query

### Custom Measurements
В каждой транзакции показаны:
- `analytics.days_processed`
- `analytics.total_games`
- `db.queries_executed`
- `cpu.calculations_performed`

## 📝 Talking Points

### При демонстрации N+1:
> "Это классическая проблема ORM, но здесь мы сделали её вручную для демо. В реальности Django/SQLAlchemy могут скрыть такие проблемы. Sentry сразу показывает паттерн."

### При демонстрации CPU Spike:
> "Неэффективный алгоритм может заблокировать весь сервис. Видим точно какая функция виновата и сколько времени тратится."

### При демонстрации Slow Aggregation:
> "MongoDB aggregation мощный инструмент, но без правильных индексов может стать bottleneck. Sentry показывает какие именно операции медленные."

## 🔧 Решения проблем

### N+1 Query Fix:
```python
# Плохо: отдельный запрос для каждой игры
for game_id in game_ids:
    game = collection.find_one({"_id": game_id})

# Хорошо: один запрос
games = collection.find({"_id": {"$in": game_ids}})
```

### CPU Spike Fix:
```python
# Плохо: генерация простых чисел для RNG
primes = generate_large_primes()

# Хорошо: использовать стандартный random
result = random.choice(symbols)
```

### Slow Aggregation Fix:
```python
# Создать индекс
collection.create_index([("timestamp", 1), ("user_id", 1)])

# Упростить pipeline
# Убрать лишние $addFields
# Использовать $project раньше
```

## 🎬 Сценарий презентации (5-7 минут)

1. **Вступление** (30 сек)
   - "Покажу как Sentry помогает находить проблемы производительности"
   - "3 реальных примера из практики"

2. **N+1 Demo** (2 мин)
   - Воспроизвести
   - Показать в Sentry
   - Объяснить impact

3. **CPU Spike Demo** (2 мин)
   - Воспроизвести
   - Показать spans
   - Обсудить решения

4. **Slow Aggregation Demo** (2 мин)
   - Воспроизвести
   - Показать missing index
   - Предложить оптимизации

5. **Выводы** (30 сек)
   - "Без Sentry поиск таких проблем занял бы часы"
   - "Видим точное место и причину"
   - "Можем приоритизировать оптимизации"

## ⚠️ Важные замечания

1. **Первый запуск** может быть медленнее - дайте системе "прогреться"
2. **Analytics Service** должен быть запущен (порт 8084)
3. **MongoDB** должна содержать данные для демо aggregation
4. Performance issues активируются **только** через Debug Panel