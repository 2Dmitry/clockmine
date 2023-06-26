FROM python:3.10

WORKDIR /clockmine

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x ./manage.py

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"