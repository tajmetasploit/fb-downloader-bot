# Use Python 3.10 as base image
FROM python:3.10.16

# Set working directory inside the container
WORKDIR /app

# Copy dependency file first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port (if you use Flask for keep-alive)
EXPOSE 8080

# Command to run your bot
CMD ["python", "main.py"]
