# 📊 Обновление системы отчетов - Точные временные интервалы

## 🔄 Изменения в системе парсинга

### ✅ Реализованные улучшения

1. **Одновременный парсинг для обеих каналов**
   - Мгновенные уведомления о новых предметах в канал обновлений
   - Полные отчеты по точному расписанию в канал отчетов

2. **Точные временные интервалы**
   - Отчеты отправляются в кратное 5 минутам время: 00:00, 00:05, 00:10, 00:15, etc.
   - Независимо от времени запуска приложения
   - Настраиваемый интервал через переменную `FULL_REPORT_INTERVAL`

3. **Улучшенное планирование**
   - Автоматический расчет следующего времени отправки
   - Учет перехода через час (59 → 00 минут)
   - Логирование времени следующего отчета

## 🔧 Конфигурация

### Переменные окружения (.env)
```bash
# Интервал полных отчетов в минутах (должен быть делителем 60)
FULL_REPORT_INTERVAL=5

# Рекомендуемые значения: 5, 10, 15, 20, 30
```

### Примеры интервалов

| Интервал | Времена отправки |
|----------|------------------|
| 5 минут  | 00:00, 00:05, 00:10, 00:15, 00:20, 00:25, 00:30, 00:35, 00:40, 00:45, 00:50, 00:55 |
| 10 минут | 00:00, 00:10, 00:20, 00:30, 00:40, 00:50 |
| 15 минут | 00:00, 00:15, 00:30, 00:45 |
| 30 минут | 00:00, 00:30 |

## 📋 Логика работы

### 1. Мониторинг новых предметов
- WebSocket подключение отслеживает изменения в реальном времени
- При обнаружении новых Divine+ предметов:
  - ✅ Мгновенная отправка в канал обновлений
  - ❌ НЕ влияет на расписание полных отчетов

### 2. Планирование полных отчетов
```python
# Алгоритм расчета следующего времени
current_minute = now.minute
interval = settings.full_report_interval

# Следующая минута, кратная интервалу
next_minute = ((current_minute // interval) + 1) * interval

# Учет перехода через час
if next_minute >= 60:
    next_minute = 0
    next_hour = (current_hour + 1) % 24
```

### 3. Содержимое отчетов

#### Канал обновлений (мгновенно при появлении)
```
⚙️[Divine] Friendship Pot (1шт) в стоке
💰Цена: 15.000.000💎

сток 00:27 мск
```

#### Канал полных отчетов (каждые 5 минут в точное время)
```
📊 Полный отчет по магазину

🔍 Найдено Divine+ предметов: 19

🌱 Семена:
• Beanstalk [Prismatic] (0шт) - 10.000.000💎 (❌ Отсутствует)
...

📅 Отчет создан: 2025-07-17 00:30:00
⏰ Следующее обновление через 5 минут
```

## 🚀 Преимущества новой системы

1. **Предсказуемость**: Отчеты всегда в одно и то же время
2. **Мгновенность**: Новые предметы не ждут расписания
3. **Синхронизация**: Все инстансы бота работают синхронно
4. **Гибкость**: Настраиваемый интервал для разных потребностей
5. **Надежность**: Независимость от времени запуска

## 📊 Тестирование

Используйте `test_scheduler.py` для проверки логики планирования:
```bash
python test_scheduler.py
```

## 🔄 Обратная совместимость

- Старые переменные окружения автоматически мигрируют
- WebSocket клиент остается без изменений
- Форматирование сообщений сохранено

## 📈 Производительность

- Минимальное потребление ресурсов при ожидании
- Один WebSocket для всех каналов
- Эффективное использование asyncio

---

**Дата обновления**: 17 июля 2025  
**Версия**: 2.0  
**Автор**: Roblox Garden Parser Team
