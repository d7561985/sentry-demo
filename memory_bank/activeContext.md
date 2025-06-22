# Active Context - Current Focus

## Current Mode: Ready for VAN

## Previous Work Completed
Scenario 1: Distributed Tracing ✅ ARCHIVED

## Active Focus
Ready to begin next scenario. Suggested: Scenario 2 - Error Tracking Suite

## Key Decisions Made (Revised)
1. **Подход**: Сценарно-ориентированная разработка
2. **БД**: Только MongoDB + Redis (упрощение)
3. **Бизнес-логика**: Минимальная слот-игра
4. **Фокус**: 6 ключевых сценариев Sentry
5. **Связность**: Все сервисы в одном trace flow

## Scenario-Driven Development
Вместо разработки по сервисам, работаем по сценариям:
1. **Distributed Tracing** - основа всего
2. **Error Tracking** - разные типы ошибок
3. **Performance** - N+1, slow queries, memory leaks
4. **Custom Metrics** - RTP, sessions, success rate
5. **Release Tracking** - regression demo
6. **Alerts** - noise reduction

## Implementation Strategy
```
Scenario → Required Services → Minimal Code → Test → Demo
```

## Next Steps
1. Начать с Scenario 1 (Distributed Tracing)
2. Создать минимальные сервисы для trace flow
3. Добавлять issues по мере реализации сценариев
4. Тестировать каждый сценарий отдельно

## Context for Next Session
- Scenario 1: COMPLETED and ARCHIVED
- Infrastructure ready for next scenarios
- 5 services with Sentry integration operational

## Available for Scenario 2:
### Already Implemented:
- API Gateway panic endpoint (`/api/v1/debug/panic/panic-test`)
- Payment Service 500 errors (10% rate)
- All service infrastructure and Docker setup

### Need to Add for Scenario 2:
- Frontend JS errors (unhandled promises)
- React error boundaries
- Additional error types demonstration

## Next Recommended Steps:
1. Start VAN mode for Scenario 2
2. Review Error Tracking requirements from sentryDemoScenarios.md
3. Plan minimal additions needed
4. Implement new error scenarios