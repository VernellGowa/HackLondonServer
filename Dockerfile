# Use Python base image
FROM python:3.11

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