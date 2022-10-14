FROM python:3.9.12-slim-buster
EXPOSE 5000
ENV FLASK_APP=app.py
WORKDIR /scrapers
COPY . /scrapers
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
#ENTRYPOINT to  stałe wejsciowe polecenie dla kontenera
ENTRYPOINT ["flask", "run"]
#CMD to metadane kontenera, nie zmienia samej zawartosci obrazu, 
#tylko mowi dockerowi, ze w momencie uruchamiania kontenera ma wykonac to polecenie
CMD ["-h", "0.0.0.0", "-p", "5000"]