FROM python:3.10

WORKDIR /clockmine

COPY ./requirements.txt /requirements.txt
RUN --mount=id=clockmine_pip_cache,type=cache,target=/root/.cache/pip pip install --default-timeout=100 -U -r /requirements.txt

COPY . .
RUN chmod +x ./manage.py

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"