# Use Python base image
FROM python:3.11

# Set working directory in container
WORKDIR /app

# Copy app files to container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Flask
EXPOSE 8080

# Run the Flask app
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "app:app"]
