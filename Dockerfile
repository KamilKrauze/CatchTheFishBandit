FROM python:3.11.5
RUN pip install --upgrade pip
COPY requirements.txt /home/
RUN pip install -r /home/requirements.txt

COPY data_framing.py /home/

ENTRYPOINT ["python"]
CMD ["/home/data_framing.py"]
EXPOSE 80