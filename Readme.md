#Публикация комиксов
Приложение, позволяющее, при запуске скрипта, автоматически делать посты в [сообществе](https://vk.com/club202725058) вконтакте.
### Как запустить
* Для запуска сайта вам понадобится Python третьей версии.
* Скачайте код с GitHub. Затем установите зависимости
```sh
pip install -r requirements.txt
```
* Создайте группу в [вк](https://vk.com/groups?tab=admin).
* Создайте приложение в [вк](https://vk.com/dev).
* Создайте файл `.env` в директории с проектом.
* Заполните `.env` следующими переменными:
```sh
VK_API_VERSION=version
VK_CLIENT_ID=client_id
VK_ACCESS_TOKEN=token
VK_GROUP_ID=group_id
LAST_COMICS_NUMBER=last_number
```
version Вы можете узнать из [документации](https://vk.com/dev/versions).

client_id можно узнать из настроек Вашего приложения вк.

Для получения token - следуйте [инструкции](https://vk.com/dev/implicit_flow_group).

group_id - можно узнать [здесь](https://regvk.com/id/).

last_number - можно получить [здесь](https://xkcd.com/json.html).

Запустите код
```sh
python main.py
```
### Цель проекта
Код написан в образовательных целях на курсе для веб-разработчиков [dvmn.org](https://dvmn.org/modules/).
