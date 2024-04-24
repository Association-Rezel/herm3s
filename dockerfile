FROM python:3.11.5-slim

# install dependencies
COPY . /

RUN  pip install --upgrade pip 
RUN  pip install -r requirements.txt

EXPOSE 80 443 8000

#entry point for "uvicorn main:app --reload"
ENTRYPOINT [ "uvicorn", "src.communication_deamon.main:app","--host", "0.0.0.0", "--reload"]


