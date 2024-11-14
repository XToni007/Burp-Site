FROM python:3.11-slim

# Set up environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install necessary system packages for aioquic and pylsqpack
RUN apt-get update && \
    apt-get install -y gcc libssl-dev libc6-dev && \
    rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Copy only the requirements file first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the entire application code
COPY . .

EXPOSE 8000
EXPOSE 5000
EXPOSE 8080
ENTRYPOINT ["python3", "src/run.py"]