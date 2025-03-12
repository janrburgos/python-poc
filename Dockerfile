# Use official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Install Pipenv
RUN pip install --no-cache-dir pipenv

# Copy Pipfile and Pipfile.lock before installing dependencies
COPY Pipfile Pipfile.lock /app/

# Install dependencies using Pipenv
RUN pipenv install --deploy --system --ignore-pipfile

# Copy the application code
COPY . /app/

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI in production mode (without --reload)
CMD ["pipenv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
