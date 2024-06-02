# Use an official Python runtime as a parent image
FROM python:3.10-slim

# install ssh-keyscan
RUN apt-get update && apt-get install -y openssh-client

# Set the working directory in the container
WORKDIR /app
# Copy the current directory contents into the container at /usr/src/app
COPY ./src/main.py /app/src/main.py
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

WORKDIR /app/src

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
