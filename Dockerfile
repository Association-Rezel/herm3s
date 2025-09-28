FROM python:3.12

# install dependencies

#copy requirements.txt BEFORE the rest of the files to not install the dependencies
# every time the code changes
COPY ./requirements.txt /hermes/requirements.txt
RUN  pip install --upgrade pip 
RUN  pip install -r /hermes/requirements.txt

#for health check
RUN apt-get update && apt-get install -y curl 

COPY ./hermes /app/hermes
COPY .env* /app

WORKDIR /app

EXPOSE 8000

ENTRYPOINT [ "uvicorn", "hermes.main:app" ]
