FROM python:3.13.1

WORKDIR /app/

COPY . .


RUN pip install -r requirements.txt --no-cache-dir

RUN python manage.py collectstatic --noinput
RUN cp -r /app/static/ /static/

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]

