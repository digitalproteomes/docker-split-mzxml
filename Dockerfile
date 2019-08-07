FROM python:3

COPY split_mzXML/main.py /usr/local/bin
RUN chmod 775 /usr/local/bin/main.py
COPY indexmzXML /usr/local/bin
