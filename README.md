# UniBot — MAX-бот для первокурсников

UniBot — backend-бот для мессенджера MAX: он регистрирует студента при первом сообщении, отвечает на FAQ, ищет документы, выдаёт контакты и принимает обращения для кураторов. В проекте **нет** OpenAI API, нейросетей или ML: знания хранятся в PostgreSQL и JSON-файлах. Модуль `app/bot/max_api.py` намеренно изолирует интеграцию с MAX, поэтому ИИ-поиск позднее можно добавить отдельным сервисом, не меняя обработчики.

## Структура

```text
app/
  api/             HTTP health/admin API и безопасный webhook MAX
  bot/             команды, обработчики и адаптер MAX Bot API
  database/        async SQLAlchemy модели и подключение PostgreSQL
  services/        FAQ, документы, поиск, рассылки
  utils/           конфигурация логирования
knowledge_base/    стартовые FAQ, контакты и документы
```

Таблицы: `users`, `faq`, `documents`, `notifications` и дополнительная `student_questions` для обращений. При старте приложения схема создаётся, а JSON-справочники идемпотентно загружаются в БД. Для production замените `create_all` на миграции Alembic.

## Команды

| Команда | Назначение |
| --- | --- |
| `/start` | приветствие и создание профиля студента |
| `/help` | список возможностей |
| `/faq` | частые вопросы |
| `/contacts` | контакты подразделений |
| `/documents` | полезные документы |
| `/map` | корпуса и адреса |
| `/search запрос` | поиск по FAQ и документам |
| `/ask вопрос` | создать обращение куратору |

Роли `student`, `curator`, `admin` хранятся в `users.role`. Идентификаторы из `ADMIN_MAX_USER_IDS` получают роль admin при первом `/start`; куратору роль назначается администратором напрямую в БД до появления отдельной панели управления.

## Локальный запуск

Требуются Python 3.11+, PostgreSQL и Redis.

```bash
cp .env.example .env
# Укажите реальные DATABASE_URL, REDIS_URL, MAX_TOKEN и MAX_WEBHOOK_SECRET в .env
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Проверка готовности: `curl http://localhost:8000/api/health`.

## Docker

```bash
cp .env.example .env
# Обязательно заполните MAX_TOKEN, MAX_WEBHOOK_URL и MAX_WEBHOOK_SECRET
docker compose up --build -d
docker compose logs -f app
```

`docker-compose.yml` поднимает приложение, PostgreSQL 16 и Redis 7 с именованными томами. Для разработки пароль PostgreSQL задан в compose-файле; на VPS замените его сильным секретом или используйте управляемую БД.

## Подключение MAX

1. Создайте бота в кабинете разработчика MAX и поместите токен **только** в `.env` как `MAX_TOKEN`. Файл уже исключён через `.gitignore`.
2. Разместите приложение на публичном HTTPS-адресе и укажите его как `MAX_WEBHOOK_URL`, например `https://bot.example.org/api/max/webhook`.
3. При создании подписки MAX задайте тот же секрет, что и `MAX_WEBHOOK_SECRET`. Webhook принимает только запросы с заголовком `X-Webhook-Secret`, сравнивая значение константно-временной проверкой.
4. Адаптер использует MAX endpoint `POST /messages` с телом `recipient.chat_id` и `text`, а для подписки — `POST /subscriptions` с `message_created`. При необходимости зарегистрируйте webhook из защищённого административного скрипта вызовом `MaxBotClient.register_webhook()`.

Обработчик ожидает событие `message_created` с полями `message.sender.user_id`, `message.recipient.chat_id`, `message.body.text`. Он также принимает эквивалентные плоские поля, чтобы адаптер было проще обновить при изменении версии MAX API. Ошибки доставки и обработки логируются, а MAX-токен никогда не выводится в логи.

## Пример диалога

```text
Студент: /start
UniBot: Добро пожаловать в UniBot — помощник первокурсника!
Студент: /search справка об обучении
UniBot: Как получить справку об обучении?
        Подайте заявление в деканат...
Студент: /ask Где получить пропуск?
UniBot: Вопрос передан куратору. Мы ответим, как только сможем.
```

## Развёртывание на VPS

1. Установите Docker Engine и Compose, склонируйте репозиторий, создайте защищённый `.env` (`chmod 600 .env`).
2. Настройте DNS-запись на VPS и reverse proxy (Nginx/Caddy) с TLS. Прокси должен передавать `/api/max/webhook` приложению на `127.0.0.1:8000`.
3. Не публикуйте PostgreSQL и Redis наружу: в текущем compose наружу выставлен только порт приложения. Ограничьте доступ к `/api/questions` и `/api/notifications` на уровне reverse proxy/VPN либо добавьте полноценную admin-аутентификацию.
4. Выполните `docker compose up --build -d`, проверьте `/api/health`, затем зарегистрируйте публичный HTTPS webhook в MAX.
5. Настройте резервное копирование тома PostgreSQL, мониторинг логов `docker compose logs`, ротацию логов и миграции Alembic перед обновлениями схемы.
