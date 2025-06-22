# Project Brief - Sentry POC for iGaming Platform

## Project Overview
Демонстрация возможностей Sentry для мониторинга критически важной iGaming платформы с фокусом на повышение надежности, производительности и пользовательского опыта.

## Business Goals
1. **Снижение операционных рисков**
   - Проактивное обнаружение проблем
   - Сокращение MTTR с 4-6 часов до 30-60 минут
   - Предотвращение потери revenue

2. **Улучшение пользовательского опыта**
   - Мониторинг 4 золотых метрик
   - Session replay для понимания проблем
   - Снижение churn rate

3. **Оптимизация разработки**
   - Быстрая локализация проблем
   - Профилирование без дополнительного кода
   - Автоматическая привязка к релизам

## Key Metrics
- MTTR: 4-6 часов → 30-60 мин
- Error Rate: 2.5% → <0.5%
- P95 Latency: 800ms → 200ms
- Alert Noise: 200/день → 10/день

## System Components
1. **API Gateway (Go)** - Entry point, auth, rate limiting
2. **Game Engine Service (Python/Tornado)** - Game logic, RNG, WebSocket
3. **User Service (Go)** - Profiles, sessions, KYC
4. **Payment Service (Node.js)** - Deposits/withdrawals, critical
5. **Analytics Service (Python)** - Metrics, fraud detection
6. **Notification Service (Go)** - Email/SMS/Push, Kafka consumer
7. **Web Frontend (Angular)** - Main gaming UI
8. **Admin Panel (React 17)** - Legacy with tech debt

## Infrastructure
- Message Queue: Kafka
- Cache: Redis
- Databases: PostgreSQL + MongoDB
- Storage: MinIO

## Sentry Integration Focus
1. Distributed tracing across services
2. Performance profiling (CPU, Memory, I/O)
3. Custom business metrics (RTP, bet volumes)
4. Error tracking with user context
5. Release tracking
6. Session replay
7. Alert optimization

## POC Approach
- **Минимальный рабочий код** - только для демонстрации Sentry
- **Никаких моков/эмуляций** - реальные связанные сервисы
- **Простая слот-игра** - примитивная симуляция без оверхеда
- **Фокус на сценариях Sentry** - не на бизнес-логике
- **Каждый сценарий** - планируется и тестируется

## Sentry Demo Scenarios (Приоритет)
1. **Distributed Tracing**
   - Запрос проходит: Frontend → Gateway → User → Game Engine → Payment
   - Показать полный trace через все сервисы

2. **Error Tracking**
   - 500 ошибка в Payment Service
   - 401 в User Service
   - JS error в Frontend
   - Panic в Go сервисе

3. **Performance Monitoring**
   - Медленный SQL запрос в User Service
   - Memory leak в React Admin Panel
   - CPU spike в Game Engine (RNG расчеты)
   - N+1 проблема в Analytics

4. **Custom Business Metrics**
   - RTP (Return to Player) tracking
   - Active sessions monitoring
   - Payment success rate

5. **Release Tracking**
   - Deploy с regression bug
   - Rollback демонстрация
   - Error spike после релиза

6. **Alert Management**
   - Критичный alert: Payment failures > 5%
   - Performance alert: P95 > 500ms
   - Error rate alert: > 1%

## Simplified Architecture
- **БД**: MongoDB (основная), Redis (кеш/сессии)
- **Минимальная бизнес-логика**: Простой слот с RNG
- **Все сервисы связаны**: Для distributed tracing
- **Intentional issues**: Встроенные проблемы для демо