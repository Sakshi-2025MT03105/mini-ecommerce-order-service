
# Use Python as the base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY database.py .

# Expose Order Service port
EXPOSE 5002

# Start Order Service
CMD ["python", "app.py"]
