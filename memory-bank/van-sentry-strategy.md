# Стратегия независимых трейсов Sentry

## Анализ проблем

### 1. Проблема с Replay
**Возможные причины:**
- Блокировщики рекламы или расширения браузера
- CSP (Content Security Policy) политики
- Проблемы с сетевыми запросами к Sentry

**Диагностика в браузере:**
```javascript
// Проверить статус replay
const replay = Sentry.getReplay();
console.log('Replay ID:', replay?.getReplayId());
console.log('Is recording:', replay?.isEnabled());
console.log('Integration:', Sentry.getClient()?.getIntegrationByName('Replay'));
```

### 2. Проблема с трейсами
**Текущая ситуация:**
- Все действия пользователя попадают в автоматические pageload/navigation транзакции
- Сложно найти конкретные действия в Sentry UI
- Нет независимых транзакций для бизнес-действий

## Решение: Стратегия независимых трейсов

### Опция 1: forceTransaction (рекомендуется)
```typescript
// Использовать опцию forceTransaction для создания независимой транзакции
await Sentry.startSpan(
  {
    name: 'user-action.slot-machine.spin',
    op: 'user-action',
    forceTransaction: true, // Форсировать создание новой транзакции
    attributes: {
      'user.id': userId,
      'bet.amount': betAmount,
    }
  },
  async (span) => {
    // Логика действия
    span?.setAttribute('result.win', result.win);
    span?.setAttribute('result.payout', result.payout);
  }
);
```

### Опция 2: startNewTrace
```typescript
// Создать полностью новый трейс, независимый от текущего контекста
await Sentry.startNewTrace(
  {
    name: 'user-action.slot-machine.spin',
    op: 'user-action'
  },
  async (span) => {
    // Вся логика выполняется в контексте нового трейса
    // Дочерние span'ы будут привязаны к этому трейсу
  }
);
```

### Опция 3: parentSpan: null
```typescript
// Явно указать, что у span нет родителя
await Sentry.startSpan(
  {
    name: 'user-action.slot-machine.spin',
    op: 'user-action',
    parentSpan: null, // Нет родительского span
    forceTransaction: true
  },
  async (span) => {
    // Логика действия
  }
);
```

## Рекомендуемая архитектура трейсов

### 1. Автоматические транзакции (оставить как есть)
- `pageload` - загрузка страницы
- `navigation` - переходы между страницами

### 2. Независимые транзакции для бизнес-действий
```
user-action.slot-machine.spin
user-action.slot-machine.debug-trigger
user-action.payment.deposit
user-action.payment.withdraw
user-action.auth.login
user-action.auth.register
user-action.metrics.refresh
```

### 3. Дочерние span'ы внутри независимых транзакций
```
user-action.slot-machine.spin
├── http.post /api/v1/spin
├── game.calculate
├── db.insert games
├── mq.publish analytics
└── ui.animation.complete
```

## Примеры реализации

### 1. Слот-машина - спин
```typescript
async spin(): Promise<void> {
  this.error = null;
  this.gameState.startSpin();
  
  // Создаем независимую транзакцию
  await Sentry.startSpan(
    {
      name: 'user-action.slot-machine.spin',
      op: 'user-action',
      forceTransaction: true,
      attributes: {
        'user.id': this.userId,
        'bet.amount': 10,
        'balance.before': this.balance()
      }
    },
    async (transaction) => {
      try {
        // HTTP запрос будет дочерним span'ом
        const result = await this.gameService.spin(this.userId, 10).toPromise();
        
        if (result) {
          transaction?.setAttributes({
            'result.win': result.win,
            'result.payout': result.payout,
            'balance.after': result.newBalance
          });
          
          // UI анимация
          await Sentry.startSpan(
            { name: 'ui.animation', op: 'ui' },
            async () => {
              await this.animateReels(result);
            }
          );
        }
        
        transaction?.setStatus('ok');
      } catch (error) {
        transaction?.setStatus('internal_error');
        throw error;
      }
    }
  );
}
```

### 2. Debug панель - триггеры
```typescript
async triggerCPUSpike(): Promise<void> {
  await Sentry.startSpan(
    {
      name: 'user-action.slot-machine.debug-cpu-spike',
      op: 'debug',
      forceTransaction: true,
      attributes: {
        'debug.type': 'cpu-spike',
        'user.id': this.userId
      }
    },
    async () => {
      // Логика триггера
    }
  );
}
```

### 3. Бизнес-метрики
```typescript
async refreshMetrics(): Promise<void> {
  await Sentry.startNewTrace(
    {
      name: 'user-action.metrics.refresh',
      op: 'user-action'
    },
    async () => {
      // Загрузка метрик
    }
  );
}
```

## Конфигурация browserTracingIntegration

Обновить конфигурацию для фильтрации автоматических span'ов:

```typescript
Sentry.browserTracingIntegration({
  // ... существующие настройки ...
  
  // Не создавать автоматические span'ы для наших кнопок
  beforeStartSpan: (options) => {
    // Пропускать автоматические клики на наших action кнопках
    if (options.name?.includes('click') && 
        options.attributes?.['ui.component']?.includes('action-button')) {
      return null;
    }
    return options;
  },
  
  // Не создавать span'ы для определенных запросов
  shouldCreateSpanForRequest: (url) => {
    // Не создавать span'ы для health checks
    if (url.includes('/health')) {
      return false;
    }
    return true;
  }
})
```

## Преимущества подхода

1. **Четкое разделение** - бизнес-действия отделены от технических транзакций
2. **Легкий поиск** - в Sentry UI можно фильтровать по `user-action.*`
3. **Бизнес-метрики** - можно строить дашборды по конкретным действиям
4. **Алерты** - можно настроить алерты на конкретные транзакции
5. **Производительность** - анализ времени выполнения бизнес-операций

## Следующие шаги

1. Проверить работу replay в браузере
2. Реализовать независимые транзакции для slot-machine
3. Добавить атрибуты бизнес-контекста
4. Настроить фильтрацию автоматических span'ов
5. Протестировать в Sentry UI