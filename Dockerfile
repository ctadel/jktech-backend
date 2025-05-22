FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the sample env file
COPY .env.sample .env

# Copy the rest of the code
COPY . .

# Default env (for SQLite fallback)
ENV ENV=PROD

# Expose port
EXPOSE 8000

# Run FastAPI app
CMD ["python", "main.py"]
