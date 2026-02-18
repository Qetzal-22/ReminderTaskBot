# Reminder Task Bot
## Functionality
Бот позваляет ставить напоминание, зацикливать, редактировать, откладывать их.

## Setting
### Config
Пример Config:
```
{
  "BOT_TOKEN_API": "YOUR TOKEN TG BOT",
  "DATABASE_URL": "sqlite:///database.db"
}
```
Путь: `.app/config/config.json`

## Command
* `/start` - Запуск бота
* `/register` - Регистрация
* `профиль`/`назад в профиль`
* `задачи`
* `просмотр задач`
* `добавить задачу`

## Control Panel
 >http://localhost:8000/tasks/