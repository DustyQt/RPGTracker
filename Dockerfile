# syntax=docker/dockerfile:1
FROM python
COPY /application .
RUN pip install -r requirements.txt
ENTRYPOINT python src/app.py