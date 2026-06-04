# Схема данных для файлов хранения

## Файл `favorites.json`

Хранит список избранных пользователей.

### Структура записи:

```json
{
  "vk_id": 123456789,
  "first_name": "Иван",
  "last_name": "Петров",
  "city": "Москва",
  "profile_url": "https://vk.com/id123456789",
  "photo_url": "https://...",
  "photos": ["url1", "url2", "url3"],
  "photos_attachments": ["photo1_1", "photo1_2", "photo1_3"],
  "photos_likes": [150, 120, 100],
  "saved_at": "2024-01-15T14:30:00"
}


Описание полей:
Поле	Тип	Описание
vk_id	int	Уникальный идентификатор пользователя ВК
first_name	str	Имя пользователя
last_name	str	Фамилия пользователя
city	str	Город пользователя
profile_url	str	Ссылка на профиль ВК
photo_url	str	URL основной фотографии
photos	array	Массив URL топ-3 фотографий
photos_attachments	array	Массив attachment-строк для отправки
photos_likes	array	Количество лайков для каждой фотографии
saved_at	str	Дата и время добавления (ISO формат)
Файл blacklist.json
Хранит список ID пользователей, которые не должны попадаться в поиске.

Файл blacklist.json
Хранит список ID пользователей, которые не должны попадаться в поиске.

Структура:
json
[123456789, 987654321, 555555555]
Простой массив целых чисел - ID пользователей ВК.

