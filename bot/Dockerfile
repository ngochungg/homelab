# Python verion
FROM python:3.12-slim

# Install nmap
RUN apt-get update && apt-get install -y nmap aircrack-ng

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

CMD ["python3", "main.py"]