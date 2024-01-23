FROM python:3.10.13-slim-bullseye

EXPOSE 5000

ENV FLASK_APP=app.py\
    FLASK_DEBUG=True

WORKDIR /scrapers

COPY . /scrapers
RUN python -m pip install --upgrade pip\
    && pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["app.py"]