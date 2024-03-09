FROM python:3.11.5
RUN pip install --upgrade pip
COPY requirements.txt /home/
RUN pip install -r /home/requirements.txt

COPY *.py /home/

ENTRYPOINT ["python"]
CMD ["/home/application.py"]
EXPOSE 80