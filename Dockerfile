FROM python:3.11.5-slim

# install dependencies

#copy requirements.txt BEFORE the rest of the files to not install the dependencies
# every time the code changes
COPY ./requirements.txt /hermes/requirements.txt
RUN  pip install --upgrade pip 
RUN  pip install -r /hermes/requirements.txt

#for health check
RUN apt update && apt install -y curl 

COPY ./hermes /hermes


EXPOSE 8000

#entry point for "uvicorn main:app --reload"
# CMD ["ls /"]
ENTRYPOINT [ "uvicorn", "hermes.main:app","--host", "0.0.0.0", "--reload"]
