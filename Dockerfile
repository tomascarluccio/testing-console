#Dockerfile for building the image for the application

# Use an official Python runtime as a parent image
FROM alpine:latest as build

# Install any needed packages specified in requirements.txt

RUN apk update
RUN apk add nano curl bash bash-doc bash-completion python3 py3-virtualenv python3-dev py3-setuptools py3-pip py3-psycopg2

# Set the working directory to /app

RUN mkdir /app  
WORKDIR /app

# Copy the current directory contents into the container at /app

ADD . /app

RUN python3 -m venv /app/
#RUN /app/bin/pip3 install -e /app/
RUN pip install -r /app/requirements.txt

RUN rm /var/cache/apk/*

# Expose the port Gunicorn will run on
EXPOSE 8000

# Start Gunicorn with your Flask app
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
