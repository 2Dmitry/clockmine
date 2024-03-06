FROM python:3.10

# WORKDIR /usr/src/app
WORKDIR /clockmine

# COPY requirements.txt /usr/src/app/
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x ./manage.py

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
