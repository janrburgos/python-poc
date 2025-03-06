# Use official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (modify as needed)


# Install Pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock for dependency caching
COPY Pipfile Pipfile.lock /app/

# Install dependencies using Pipenv
RUN pipenv install --deploy --system --ignore-pipfile

# Copy the rest of the application code
COPY . /app/

# Expose FastAPI’s default port
EXPOSE 8000