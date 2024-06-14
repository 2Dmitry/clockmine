## About
Автоматизация учета затраченного времени между сервисом Clockify и Redmine.

Трекать время, затраченное на работу, считаю очень важным аспектом и для работодателя и для личного удовлетворения работой, для личной оценки выполненной работы. В дни повышенной активности, когда задачи сыпятся со всех сторон, когда много разных контекстов, задача фиксации потраченного времени уходит на последний план.

Данная утилита предназначена для того, чтобы пользоваться удобным сервисом для фиксации затраченного времени и чтобы удобно переносить это время в task-tracker, в текущей реализации - Redmine.

## Почему Clockify?
Я попробовал много разных приложений для отслеживания времени, и Clockify не хранит данные локально и достаточно юзерфрендли.

P.S. спасибо Виктору Ф. за то, что когда-то порекомендовал этот сервис

### Минусы Clockify
1. если пользоваться GoogleChrome расширением, то иногда вылетает из аккаунта, но таймер не останавливается, и время не "обнуляется".
2. доступность сервиса зависит доступности сервисов Google на территории РФ, 1-2 раза за год были проблемы с доступом к [tracker](https://app.clockify.me/tracker).
3. громоздкий интерфейс на официальной странице из-за того, что Clockify - полноценный сервис по управлению проектами.

## Установка (до 15 минут)

### 1. Атака клонов
```bash
git clone https://github.com/milov-dmitriy/clockmine.git
cd clockmine
cp ./deploy/.env ./.env
```

### 2. Учетные записи
#### 2.1 Redmine (API-ключ)
- копируем [`API-ключ`](https://redmine.sbps.ru/my/api_key) для вашей учетной записи Redmine;
- присваиваем скопированное значение переменной `REDMINE_API_KEY` в `.env` файле.
#### 2.2 Clockify
##### 2.2.1 API-ключ
- создаем или логинимся (если уже есть) в учетную запись [`Clockify`](https://app.clockify.me/en/login);
- переходим в [`настройки`](https://app.clockify.me/user/settings) и перематуываем в самый низ сраницы;
- генерируем API-ключ в соответствующем поле и копируем сгенерированное значение в переменную `CLOCKIFY_API_KEY` в `.env` файле.
##### 2.2.2 Расширение
В магазине расширений GoogleChrome есть соответствующие расширение Clockify, однако оно гораздо менее удобное, чем полная версия сервиса [tracker](https://app.clockify.me/tracker). Расширение не рекомендую.

### 3. Предварительная настройка Clockmine
- **если** ваша таймзона отличается от `Europe/Moscow`, **то** в `.env` файле меняем значение переменной `TIMEZONE` на таймзону из списка разрешенных таймзон, перечисленных в файле `timezones.py`;
  * Default: таймзоной по умолчанию выбрана `Europe/Moscow`
- _(по желанию)_ можно в .env файле в переменной `REDMINE_URL_TIME_ENTRY` указать любую ссылку, которая будет выводится в консоль сразу после того, как вы успешно выполните команду `push` (о которой мы поговорим чуть позже);
  * Default: в консоль выводится [`такая`](https://redmine.sbps.ru/time_entries?utf8=%E2%9C%93&set_filter=1&sort=spent_on%3Adesc&f%5B%5D=spent_on&op%5Bspent_on%5D=w&f%5B%5D=user_id&op%5Buser_id%5D=%3D&v%5Buser_id%5D%5B%5D=me&f%5B%5D=&c%5B%5D=created_on&c%5B%5D=hours&c%5B%5D=activity&c%5B%5D=user&c%5B%5D=project&c%5B%5D=issue&group_by=spent_on&t%5B%5D=hours&t%5B%5D=) ссылка
- в переменной `REDMINE_ACTIVITIES_NOT_ALLOWED` в `.env` файле указываем в формате python-списка деятельность, которой вы **не** пользуетесь при проставлении трудочасов.
  * Default: нет запрещенных деятельностей

### 4. Разворачивание
Сбилдим контейнер:
```bash
chmod u+x ./upgrade.sh
./upgrade.sh
```
Команда ниже импортирует деятельность из Redmine в Clockify:
```bash
docker-compose exec app ./manage.py init
```

### 5. Как пользоваться
1. Заходим на страницу [tracker](https://app.clockify.me/tracker);
2. Обязательно вводим в поле: .* <номер задачи из редмайн> .* <символы `-ci`> <произвольный комментарий>
   `.*` - любое кол-во любых символов, кроме цифр
4. Запускаем таймер;
5. Останавливаем таймер.

### 6. Нюансы
1. В описании/заголовке затреканного времени в Clockify обязательно должен быть номер Redmine-задачи, к которой у вас есть доступ в Redmine, символы `-ci` обязательны и нужны для отделения комментария от деятельности, комментарий обязателен
2. Для успешного выполнения команды `push` (`docker-compose exec app ./manage.py push`) каждая распаршенная запись из Clockify должна иметь `Y` в колонке `Ok?`. `Y` означает, что запись из Clockify может быть успешно перенесена в Redmine.
3. **Если** у вас запущен таймер, **то** при выполнении одной из команд (`push` или `report`) clockmine самостоятельно остановит запущенный таймер.
4. Время будет затрекано в Redmine в ту дату, в которую был сделан старт таймера в Clockify.
- **Если** вы работали в пятницу и забыли затрекать, **то**, после успешного выполнения команды "push" в понедельник, время будет затрекано в пятницу.
- **Если** вы начали трекать время в 23:30 вторника, а закончили в 1:00 среды, **то** время будет затрекано во вторник.
5. Информация о затреканном времени удаляется из Clockify сразу после того, как была успешно перенесена в Redmine.
6. **Если** вы не выбрали никакой тег (аналог "Деятельность" в Redmine) в записи Clockify, **то** этой записи будет автоматически присвоен тег/деятельность "Разработка".
7. **Если** вы указали несколько тегов в Clockify, **то** будет взята первая по списку деятельность.

### 7. Варианты команд
```
docker-compose exec app ./manage.py --help
docker-compose exec app ./manage.py init
docker-compose exec app ./manage.py report
docker-compose exec app ./manage.py report --coeff 0.5
docker-compose exec app ./manage.py report --target 5.0
docker-compose exec app ./manage.py push
docker-compose exec app ./manage.py push -c 0.5
docker-compose exec app ./manage.py push -t 5.0
```
- введенное вами число пройдет валидацию только, если будет больше нуля;
- `report` - получить информацию о затреканном времени в Clockify;
- `push` - перенести затреканное время из Clockify в Redmine и удалить всё затреканное время в Clockify;
- `coeff` - умножает каждое затреканное время на значение coeff, т.е. можно легко затрекать -50% (`-с 0.5`) от суммарного времени и **не** высчитывать это значение самому;
- `target` - указывает итоговое суммарное значение затреканного времени, т.е. если вы суммарно затрекали 6.0h, но знаете, что 30m оказывали консультации во многих задачах по чуть-чуть и никак не смогли затрекать это время, то указывайте `--target 6.5`.

## TODO
1. Прикрутить ТГ-бота, через который можно было бы выполнять все команды, который бы трекал время по расписанию, например, или напоминал что надо затрекать.
2. logger вместо print
3. ...
