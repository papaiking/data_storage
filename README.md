# Data Storage Service

This is a FastAPI application that provides APIs to store and retrieve objects/binary files.

## Features

- Store data blobs via a POST request.
- Retrieve data blobs via a GET request.
- Bearer token authentication.
- Configurable storage backend (local filesystem, Amazon S3 or Postgresql database).
- Asynchronous operations.

## Project Structure

```
$ project_folder/
├───logs/
├───_blob_storage/
├───app/
│   ├───__init__.py
│   ├───config.py
│   ├───config_template.py
│   ├───auth.py
│   ├───storage.py
│   ├───database.py
│   ├───models.py
│───routers/
│   ├───__init__.py
│   └───blob.py
│───tests/
│   ├───__init__.py
│   └───test_http_blob.py
├───main.py
├───requirements.txt
├───start.sh
└───README.md
└───docker-compose.yaml
└───Dockerfile
└───.dockerignore
```

## Setup

0. **Environment:**

    Python 3.12.0

1.  **Create a virtual environment:**

    ```bash
    python -m venv .venv --prompt hams
    source .venv/bin/activate
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the application:**

    Create a `.env` file in the project directory and override the default settings from `app/config.py`.

    **Example `.env` file:**

    ```
    SECRET_KEY = "a-very-secret-key"

    # Local storage config
    LOCAL_STORAGE_PATH = "/path/to/your/storage"

    # Configuration for S3 storage
    S3_ACCESS_KEY_ID = "xxxxx"
    S3_SECRET_ACCESS_KEY = "xxxxxx"
    S3_BUCKET_NAME = "xxxxx"
    S3_REGION_NAME = "xxxxx"

    ACTIVE_STORAGE="local"  # or "database"

    # Settings for Postgresql database storage
    DB_USER = "your_db_user"
    DB_PASSWORD = "your_db_password"
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_NAME = "your_db_name"
    ```

4.  **If using Postgresql, create the database:**

    Make sure you have a running Postgresql server and create a database with the name you specified in the configuration.

## Configure Amazone S3
    - Goto S3 service, create bucket, we'll got bucket name and bucket region name
    - Edit bucket policy with S3 actions and resource to created bucket
    - Goto IAM User service, create user, then create user's credentials (Access key and Secret Access key)
    - Assign permissions to this user with S3 full access permissions


## Running the Application manually

1.  **Start the server in development mode:**

    Navigate to the project directory and run the following command:

    ```bash
    uvicorn main:app --reload
    ```

    The application will be available at `http://127.0.0.1:8000`.

2.  **Start the server in production mode:**
    - Update configure in `start.sh` file
    - Change file permission to allow execute: 744
    - Start app from project dir:


    ```bash
    ./start.sh
    ```

3. **Running unit test**
    - Run test: pytest tests/test_http_blob.py::{test_case}
    - test_case should be one of following:
        1. test_http_store_and_retrieve_binary_blob
        2. test_retrieve_nonexistent_blob
        3. test_store_blob_invalid_token
        4. test_store_blob_invalid_base64

## Running with Docker

1.  **Prerequisites:**

    *   Docker and Docker Compose installed.
    *   A `.env` file in the project root with the following minimum variables:
        ```
        ACTIVE_STORAGE=database
        DB_USER=myuser
        DB_PASSWORD=mypassword
        DB_HOST=db      # Fixed
        DB_PORT=5432
        DB_NAME=mydatabase
        ```

2.  **Start the application:**

    ```bash
    docker-compose up
    ```

    The application will be available at `http://127.0.0.1:8000`.    

## API Usage

You need to include an `Authorization` header with a bearer token in your requests. The token is the `SECRET_KEY` you've set in your configuration.

**Header:** `Authorization: Bearer 76134SBNVDSDHGWF25462567523`

### Store a Blob

-   **Method:** `POST`
-   **Endpoint:** `/v1/blobs`
-   **Body:**

    ```json
    {
      "id": "my-unique-blob-id",
      "data": "SGVsbG8gV29ybGQh"
    }
    ```

-   **Response (201 Created):**

    ```json
    {
        "message": "Blob stored successfully"
    }
    ```

### Retrieve a Blob

-   **Method:** `GET`
-   **Endpoint:** `/v1/blobs/{id}`

-   **Example Request:**

    ```
    GET http://127.0.0.1:8000/v1/blobs/my-unique-blob-id
    ```

-   **Response (200 OK):**

    ```json
    {
      "id": "my-unique-blob-id",
      "data": "SGVsbG8gV29ybGQh",
      "size": 13,
      "created_at": "2023-10-27T10:00:00Z"
    }
    ```