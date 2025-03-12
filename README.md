# FastAPI App

## Overview
This is a Dockerized FastAPI application to be used for prototyping or creating POCs. The application runs in a container and uses Pipenv for dependency management. The provided Makefile includes useful commands to build, update, start, and interact with the application efficiently.

## Prerequisites
Before running the application, ensure you have the following installed on your system:
- [Docker](https://docs.docker.com/get-docker/)
- [Make](https://www.gnu.org/software/make/)

## Setup Instructions
Follow these steps to get the FastAPI application up and running.

### 1. Build the Docker Image
Build the Docker image using the `build` command. This will create a Docker container named `fastapi-local-app`.
```sh
make build
```

### 2. Update Dependencies
If you need to update or lock dependencies within the Pipenv environment, use:
```sh
make update
```
This will ensure that the `Pipfile.lock` is up to date. Don't forget to rebuild the Docker image after updating `Pipfile.lock` by re-running `make build`.

### 3. Set Up Environment Variables
Copy the `.env-local` file to `.env` to load environment variables:
```sh
make dotEnvLocal
```
The `.env-local` is used to keep track of the environment variable keys currently required to make the app run properly.

### 4. Start the FastAPI Application
Run the application using the following command:
```sh
make start
```
This will start the FastAPI application inside a Docker container and expose it on port `8000`.

### 5. Access the API
Once the application is running, you can access the API via:
- Open in a browser: [http://localhost:8000](http://localhost:8000)
- Interactive API documentation (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- Alternative API docs (ReDoc): [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Open a Shell in the Running Container
To interact with the running container, use:
```sh
make shell
```
This opens a Bash shell inside the `fastapi-app` container.

## Stopping the Application
Since the container is run with `--rm`, it will be automatically removed when stopped. To stop the application, simply press `Ctrl + C` if running in the foreground.

## Unit Testing
To run all unit tests, run the following command:
```sh
make test
```
To run tests from a specific files, refer to this sample command:
```sh
make test tests/test_main.py
```
To run a specific test function, refer to this sample command:
```sh
make test tests/test_main.py::test_get_root
```
You can test multiple files and functions by separating them with spaces.
```sh
make test tests/test_main.py tests/routers/test_arithmetic.py::test_add
```
After running the tests, the coverage report will be generated in `htmlcov/index.html`.

## Auto Formatting and Linting
To auto-format and auto-lint the code, run the following command:
```sh
make format
```

## Additional Notes
- The `make start` command runs the container temporarily. If you want to run it in detached mode, modify the Makefile to include the `-d` flag in the `docker run` command.
- Ensure that the `.env` file contains all necessary environment variables before starting the app.