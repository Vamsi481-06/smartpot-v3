# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the contents from your local "SmartPot" folder to the Docker image
COPY . /app/

# Expose port
EXPOSE $PORT

# Run the application:
CMD ["uvicorn", "API_Deploy:app", "--host", "0.0.0.0", "--port", "$PORT"]
