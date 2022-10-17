# start from the official Python 3.10 image
FROM python:3.10

# set current working directory to /code
WORKDIR /code

# copy only the requirements files (to take advantage of Docker cache)
COPY ./requirements.txt /code/requirements.txt
COPY ./dev_requirements.txt /code/dev_requirements.txt

# install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/dev_requirements.txt

# copy the app inside the /code directory
COPY ./app /code/app

# run the command to start the uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
