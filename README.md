# Платформа обмена (Barter Exchange Platform)

**Barter Exchange Platform** — это веб-приложение, позволяющее пользователям размещать объявления и обмениваться товарами без использования денежных средств.

(Сделано для тестового задания)

## 🚀 Возможности

* Размещение и просмотр объявлений об обмене
* Создание предложений обмена между пользователями
* Управление своими объявлениями и предложениями
* Интуитивно понятный веб-интерфейс

## 🛠️ Технологии

* **Backend**: Python, Django
* **Frontend**: HTML, CSS (Django Templates)
* **База данных**: SQLite (по умолчанию)
* **Управление зависимостями**: pip, requirements.txt

## 📁 Структура проекта

```

barter-exchange-platform/
├── ads/                # Приложение для управления объявлениями
├── project/            # Конфигурации проекта
├── templates/          # HTML-шаблоны
├── manage.py           # Основной управляющий скрипт Django
├── requirements.txt    # Список зависимостей проекта
└── README.md           # Документация проекта
```



## ⚙️ Установка и запуск

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/javoxirone/barter-exchange-platform.git
   cd barter-exchange-platform
   ```

2. Создайте и активируйте виртуальное окружение:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Unix или MacOS
   venv\Scripts\activate     # Для Windows
   ```



3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Примените миграции базы данных:

   ```bash
   python manage.py migrate
   ```

5. Создайте суперпользователя:

   ```bash
   python manage.py createsuperuser
   ```

6. Запустите сервер разработки:

   ```bash
   python manage.py runserver
   ```

7. Откройте в браузере: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

8. Запустите тесты:

   ```bash
   pytest
   ```
   или
   ```bash
   pytest -v
   ```

## 📌 Примечания

* Для доступа к административной панели перейдите по адресу: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
* Убедитесь, что у вас установлены Python 3.11 или выше и pip.

## 🤝 Контакты

Разработчик: [Javohir Nurmatjonov](https://github.com/javoxirone)

Если у вас есть предложения или вы нашли ошибку, пожалуйста, создайте issue или отправьте pull request.

---

*Этот файл README.md предназначен для предоставления общей информации о проекте и может быть дополнен более подробной документацией по мере развития проекта.*

[1]: https://github.com/ArT-191/barter-platform?utm_source=chatgpt.com "ArT-191/barter-platform - GitHub"
[2]: https://gist.github.com/JavoxirOne?utm_source=chatgpt.com "javoxirone’s gists · GitHub"
