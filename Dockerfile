# syntax=docker/dockerfile:1
FROM python
COPY /application /var/www
RUN pip3 install -r /var/www/requirements.txt
EXPOSE 5000 
CMD ["python3", "app.py"]