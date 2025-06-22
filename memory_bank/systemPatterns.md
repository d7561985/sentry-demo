# System Patterns - Simplified POC Architecture

## POC Focus
**Сценарии Sentry, не бизнес-логика!**

## Architecture Pattern
Простые микросервисы для демонстрации Sentry:
- REST communication для distributed tracing
- Минимум async - только где нужно для демо
- Все сервисы связаны для показа трейсинга
- Встроенные проблемы для демонстрации

## Integration Points
1. **Synchronous Flow (Main Demo)**
   ```
   User → Frontend → Gateway → User Service → Game Engine → Payment
   ```
   - Trace propagation через HTTP headers
   - Каждый сервис добавляет span
   - Видимость всего flow в Sentry

2. **Simplified Async**
   - Redis pub/sub для game events (опционально)
   - Простая очередь для notifications

## Data Patterns (Simplified)
- **MongoDB**: Все данные (users, games, payments)
- **Redis**: Sessions и temporary data
- **No PostgreSQL**: Упрощаем для POC
- **No MinIO**: Статика в коде

## Intentional Issues for Demo
1. **Payment Service**
   - Random 500 errors (10% rate)
   - Slow external API simulation (2-5s delay)
   
2. **User Service**
   - N+1 query problem
   - Missing index on MongoDB query
   
3. **Game Engine**
   - CPU spike on RNG calculation
   - Memory allocation issues
   
4. **Admin Panel**
   - Memory leak in React components
   - Slow re-renders

## Sentry Integration Strategy
1. **Scenario-Based Development**
   - Каждый сервис = демо сценарий
   - Встроенные проблемы
   - Легко воспроизводимые issues

2. **Trace Flow**
   ```
   1. User clicks "Spin" in Frontend
   2. → API Gateway (add user context)
   3. → User Service (check balance)
   4. → Game Engine (calculate result)
   5. → Payment Service (update balance)
   6. → Response back through chain
   ```

3. **Metrics to Track**
   - Spin success rate
   - Average spin time
   - Payment processing time
   - Error rates by service