FROM python:3.10.9-alpine@sha256:ef5536e8f22c1697807cabe68765567cea4558b4b3f3287e2277b336cf2273a5

WORKDIR /clockmine

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD [ "python", "main.py" ]