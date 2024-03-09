FROM python:3.11.5
RUN pip install --upgrade pip
COPY requirements.txt /home/
RUN pip install -r /home/requirements.txt

COPY *.py /home/
COPY *.json /home/
COPY *.config.js* /home/

COPY templates/*.* /home/templates/
COPY static /home/static/ 

RUN npm install
RUN npm run create-css

ENTRYPOINT ["python"]
CMD ["/home/app.py"]
EXPOSE 80