# Use Python base image
FROM python:3.11

# Install system dependencies required by OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Set working directory in container
WORKDIR /app

# Copy app files to container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose port for Flask
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]