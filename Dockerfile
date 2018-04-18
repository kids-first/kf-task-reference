FROM python:3.6

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py app.py

EXPOSE 8282
ENV FLASK_APP=app.py

CMD [ "flask", "run", "-h", "0.0.0.0", "-p", "8282" ]
