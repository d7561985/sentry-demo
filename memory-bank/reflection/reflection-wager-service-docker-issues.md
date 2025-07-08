# Reflection: Wager Service Docker Build Issues

## Date: 2025-01-07
**Task**: PHP/Symfony Wager Service Implementation
**Phase**: REFLECT
**Issue**: Docker build failures preventing deployment

## Problem Analysis

### 1. Root Cause: Version Incompatibilities
```
MongoDB Extension: 
- Installed: 2.1.1
- Required by doctrine/mongodb-odm-bundle 4.6: ^1.5
- Required by doctrine/mongodb-odm-bundle 5.0: ^1.16
```

### 2. Cascading Issues
- Upgrading to mongodb-odm-bundle 5.0 requires Symfony 6.4+
- Symfony 6.4 has different bundle requirements
- Sentry bundle 4.14 incompatible with newer setup
- MakerBundle loaded in production (should be dev only)

### 3. Environment Challenges
- No composer.lock = unstable dependencies
- Network issues during composer install
- Complex PHP extension requirements

## Solutions Evaluated

### Option 1: Fix PHP Dependencies ❌
**Attempted**:
- Upgrade Symfony to 6.4
- Upgrade/downgrade various bundles
- Use --ignore-platform-req flag

**Result**: Circular dependency hell

### Option 2: Rewrite in Node.js ✅
**Pros**:
- Consistent with payment-service
- Simpler Docker builds
- Native MongoDB driver
- Better Sentry SDK support

**Cons**:
- Rewrite required
- Loss of Symfony features

### Option 3: Rewrite in Go ✅
**Pros**:
- Consistent with gateway, user, notification services
- Fast and efficient
- Simple deployment
- Good MongoDB driver

**Cons**:
- More verbose code
- Less framework magic

### Option 4: Mock Service 🤔
**Pros**:
- Fastest to implement
- No dependency issues
- Sufficient for POC demo

**Cons**:
- Less realistic
- No actual MongoDB integration

## Decision Matrix

| Criteria | Fix PHP | Node.js | Go | Mock |
|----------|---------|---------|-----|------|
| Time to implement | 🔴 High | 🟡 Medium | 🟡 Medium | 🟢 Low |
| Consistency | 🔴 Low | 🟡 Medium | 🟢 High | N/A |
| Maintainability | 🔴 Low | 🟢 High | 🟢 High | 🟡 Medium |
| POC Value | 🟢 High | 🟢 High | 🟢 High | 🟡 Medium |

## Recommendation - UPDATED

**Решение**: Обновить до **Symfony 7**
- Symfony 7 поддерживает последние версии всех зависимостей
- Решит проблемы совместимости с MongoDB extension 2.1.1
- Современный PHP стек остается в проекте
- Сохраняем всю написанную бизнес-логику

**План действий**:
1. Обновить composer.json до Symfony 7.*
2. Обновить Sentry bundle до последней версии
3. Использовать последние версии Doctrine MongoDB ODM
4. Исправить конфигурационные файлы под Symfony 7

## Lessons Learned

1. **Technology Stack Consistency Matters**
   - Mixed stacks increase complexity
   - Deployment becomes harder
   - Knowledge sharing suffers

2. **PHP Containerization is Complex**
   - Many system dependencies
   - Extension version management
   - Composer quirks

3. **POC vs Production Trade-offs**
   - POC should prioritize speed
   - Don't over-engineer
   - Focus on demonstrating value

## Action Items

1. **Immediate**: Create Node.js version of wager service
   - Copy structure from payment-service
   - Implement same API endpoints
   - Use native MongoDB driver

2. **Future**: Standardize on 2-3 languages max
   - Go for high-performance services
   - Node.js for rapid development
   - Frontend frameworks as needed

## Code Preservation

All PHP code is preserved in:
- `/services/wager-service/` - Full implementation
- Integration code in other services remains valid
- API contracts are defined and stable