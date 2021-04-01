# Use an official Python runtime as an image
FROM python:3.6

EXPOSE 8089

WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
COPY aws_service.py /app
COPY bulk_service.py /app
COPY default.sql /app
COPY config.ini /app
COPY mySQL.py /app
COPY service.py /app

RUN pip install -r requirements.txt

# Run app.py when the container launches
CMD python service.py