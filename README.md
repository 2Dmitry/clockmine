DEV
python -m venv venv
pip install --upgrade pip
*activate venv*
pip install -r requirements.txt


1.1. sign in redmine
1.1. sign in clockify
*TODO тут гайд как правильно настроить Клокифу: добавить деятельность и как добавить кнопку в редмайн задачах*
2. rename example.env -> .env
3. set api-keys from yours accounts
4. docker compose build && docker compose up -d
5. use commands

TODO разнеси по папкам файлы, мол деплой, приложение и всё такое
TODO сделай авторестарт контейнера при изменинии питонокода
TODO все нужные настройки клокифай должны заполняться 1 командой
TODO проставлять всем кто будет использовать случайную аватарку из гачи

docker-compose up -d
docker-compose exec app ./manage.py report
docker-compose exec app ./manage.py push
docker-compose exec app ./manage.py push --coeff 1.073
docker-compose exec app ./manage.py push --target 5.50