FROM python:alpine



WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY statusInfo.py ./

CMD ["python3","./statusInfo.py"]




