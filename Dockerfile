FROM python:3.11.5
RUN pip install --upgrade pip
COPY requirements.txt /home/
RUN pip install -r /home/requirements.txt

COPY map.py /home/

ENTRYPOINT ["python"]
CMD ["/home/map.py"]
EXPOSE 80