FROM python:3.11.5-slim

# install dependencies

COPY ./requirements.txt /hermes/requirements.txt
RUN  pip install --upgrade pip 
RUN  pip install -r /hermes/requirements.txt
COPY . /hermes

EXPOSE 80 443 8000

#entry point for "uvicorn main:app --reload"
# CMD ["ls /"]
ENTRYPOINT [ "uvicorn", "hermes.src.main:app","--host", "0.0.0.0", "--reload"]
