# Claude Computer Use

A comprehensive system that enables interaction with an AI agent for computer use through a web interface.

## Overview

This project consists of three main services:

1. **AI-Model Service** - A stateless service with an AI agent enhanced with FastAPI for API exposure (Python/FastAPI)
2. **Backend Service** - A stateful service that manages chat history, file uploads, user sessions, and communication with the AI-Model service (Python/FastAPI)
3. **Frontend** - A user interface for client interaction with the application (NextJS/ReactJS/Bootstrap)

## System Architecture

#### Database ERP Diagram

![Database ERP Diagram](https://github.com/shakir-fattani/claude-computer-use/blob/main/erp-diagram-for-database.png)

#### Component Architecture

The system is built on a three-tier architecture with clear separation of concerns:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   Frontend    │     │    Backend    │     │   AI Model    │
│   (NextJS)    │◄───►│   (FastAPI)   │◄───►│   Service     │
└───────────────┘     └───────┬───────┘     └───────────────┘
                              │
                      ┌──────-▼──────┐
                      │  Database    │
                      │  (Postgres)  │
                      └────────────-─┘
```

#### Data Flow Diagram

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  User    │ request │  Web UI  │ API call│  Backend │ AI query│ AI Model │
│ Browser  │────────►│ Frontend │────────►│  Server  │────────►│ Service  │
└──────────┘         └──────────┘         └──────────┘         └──────────┘
     ▲                                         │                    │
     │                                         │                    │
     └─────────────────────────────────────────┴────────────────────┘
                            response
```

#### Authentication Flow

```
┌──────────┐         ┌──────────┐         ┌─────────----------─┐
│  User    │ login   │  Backend │ validate│  Auth              │
│ Browser  │────────►│  Server  │────────►│ Service (internal) │
└──────────┘         └──────────┘         └──────────----------┘
     ▲                    │                    │
     │                    │                    │
     └────────────────────┴────────────────────┘
            JWT token & expiration
```

#### Chat Message Flow

```
┌──────────┐       ┌──────────┐       ┌──────────┐       ┌──────────┐
│  User    │ send  │  Backend │ store │ Database │       │ AI Model │
│ Message  │──────►│  Server  │──────►│          │       │ Service  │
└──────────┘       └──────────┘       └──────────┘       └──────────┘
                        │                                      ▲
                        │                                      │
                        └──────────────────────────────────────┘
                                 forward for processing

┌──────────┐       ┌──────────┐       ┌──────────┐
│  User    │◄──────│  Backend │◄──────│ AI Model │
│ Browser  │ show  │  Server  │ send  │ Service  │
└──────────┘       └──────────┘       └──────────┘
                        │
                        ▼
                   ┌──────────┐
                   │ Database │
                   │ (store)  │
                   └──────────┘
```

## Prerequisites

- Docker
- Docker Compose

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/shakir-fattani/claude-computer-use.git
cd claude-computer-use
```

### 2. Build the AI-Model Baseline Image

```bash
cd ai-model
docker build . -f Dockerfile.baseline -t enterprise-computer-use:baseline
cd ..
```

### 3. Start the Services

```bash
docker-compose up --build
```

> **Note:** If the virtual desktop fails to start initially, try running the same command again or use the following to clean up existing containers first:
>
> ```bash
> docker stop $(docker ps -aq) && docker rm $(docker ps -aq) && docker-compose up --build
> ```

### 4. Create an Admin User

```bash
# Access the backend container shell
docker exec -it backend bash

# Create a superuser
python scripts/create_user.py --username shakir --email shakir@gmail.com --password shakir123 --first-name shakir --last-name fattani --superuser

# Exit the container shell
exit
```

### 5. Access the Application

Open your browser and navigate to [http://localhost:3000/login](http://localhost:3000/login)

## API Documentation

The system exposes RESTful APIs for integration. For detailed API documentation:

- Backend API: [http://localhost:8010/docs](http://localhost:8010/docs)
- AI-Model API: [http://localhost:8020/docs](http://localhost:8020/docs)

## Development

### Project Structure

```
claude-computer-use/
├── ai-model/         # AI-Model service
├── backend/          # Backend service
├── frontend/         # Frontend application
└── docker-compose.yml
```

### Environment Variables

Configuration is handled through environment variables defined in the docker-compose.yml file.

## Troubleshooting

- **Services not starting properly:** Try restarting Docker or rebuilding individual services
- **Database connection issues:** Ensure the database service is running correctly
- **Authentication problems:** Verify that you're using the correct credentials

## API documentation

### AI Model Service API Documentation

This document outlines the available endpoints for interacting with the AI model service.

#### Base URL

```
http://localhost:8000
```

#### Endpoints

##### Send Message

Sends a message to the AI model and receives a response.

**Endpoint:** `POST /send_message`

**Headers:**

```
Accept: application/json
Content-Type: application/json
```

**Request Body:**

```json
{
  "messages": [{ "role": "user|assistant|system", "content": "message text" }]
}
```

The `messages` array contains message objects with:

- `role`: Can be "user", "assistant", or "system"
- `content`: The text content of the message

**Example Request:**

```http
POST http://localhost:8000/send_message
Accept: application/json
Content-Type: application/json

{
    "messages": [
        { "role": "user", "content": "hi" }
    ]
}
```

**Expected Response:**

```json
{
  "response": [
    { "role": "assistant", "content": "Hello! How can I assist you today?" }
  ]
}
```

#### Usage Notes

- The AI model service expects messages in a specific conversation format, with each message having a role and content.
- The service maintains conversation context based on the sequence of messages sent.
- You can send multiple messages in a single request to provide conversation history for context.
- For complex queries, it's recommended to include relevant previous messages in the conversation.

#### Example: Multi-turn Conversation

```http
POST http://localhost:8000/send_message
Accept: application/json
Content-Type: application/json

{
    "messages": [
        { "role": "system", "content": "You are a helpful assistant." },
        { "role": "user", "content": "What can you tell me about machine learning?" },
        { "role": "assistant", "content": "Machine learning is a branch of artificial intelligence that focuses on building systems that learn from data." },
        { "role": "user", "content": "What are some common algorithms?" }
    ]
}
```

This request sends the complete conversation history to maintain context when the model generates its response to the final question.

### Backend system api Document

This document outlines the available endpoints for the application, including authentication, user management, file operations, and chat interactions.

#### Base URL

```
http://localhost:8010/api/v1
```

#### Authentication

##### Login

Authenticates a user and returns an access token.

**Endpoint:** `POST /auth/login`

**Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "username": "username",
  "password": "password"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Example:**

```http
POST http://localhost:8010/api/v1/auth/login
Content-Type: application/json

{
    "username": "shakir",
    "password": "shakir123"
}
```

#### Users

##### Get Users

Retrieves a list of all users.

**Endpoint:** `GET /users/`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {access_token}
```

**Example:**

```http
GET http://localhost:8010/api/v1/users/
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Files

##### List Files

Retrieves all files for the authenticated user.

**Endpoint:** `GET /files/`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {access_token}
```

**Example:**

```http
GET http://localhost:8010/api/v1/files/
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

##### Upload File

Uploads a file to the server.

**Endpoint:** `POST /files/upload/`

**Headers:**

```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Example:**

```http
POST http://localhost:8010/api/v1/files/upload/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="example.pdf"
Content-Type: application/pdf

< ./example.pdf
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

##### Get File by ID

Retrieves a specific file by its ID.

**Endpoint:** `GET /files/{file_id}/`

**Headers:**

```
Authorization: Bearer {access_token}
```

**Example:**

```http
GET http://localhost:8010/api/v1/files/cee387d1-c4f5-4dbe-84d6-f61bdd2780b4/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

##### Delete File

Deletes a specific file by its ID.

**Endpoint:** `DELETE /files/{file_id}`

**Headers:**

```
Authorization: Bearer {access_token}
```

**Example:**

```http
DELETE http://localhost:8010/api/v1/files/cee387d1-c4f5-4dbe-84d6-f61bdd2780b4
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Chats

##### Create Chat

Creates a new chat with an initial message.

**Endpoint:** `POST /chats/`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {access_token}
```

**Request Body:**

```json
{
  "initial_message": "Message content",
  "initial_role": "user"
}
```

**Example:**

```http
POST http://localhost:8010/api/v1/chats/
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
    "initial_message": "Hello, I need help analyzing some data",
    "initial_role": "user"
}
```

##### List User Chats

Retrieves all chats for the authenticated user.

**Endpoint:** `GET /chats/`

**Headers:**

```
Authorization: Bearer {access_token}
```

**Example:**

```http
GET http://localhost:8010/api/v1/chats/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

##### Get Chat with History

Retrieves a specific chat with its full message history.

**Endpoint:** `GET /chats/{chat_id}`

**Headers:**

```
Authorization: Bearer {access_token}
```

**Example:**

```http
GET http://localhost:8010/api/v1/chats/b5c3b2aa-0945-4ee8-9d17-0ffe388d3529
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

##### Add Message to Chat

Adds a new message to an existing chat.

**Endpoint:** `POST /chats/{chat_id}/history`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer {access_token}
```

**Request Body:**

```json
{
  "role": "user",
  "message": "Message content",
  "extra_data": {}
}
```

**Example:**

```http
POST http://localhost:8010/api/v1/chats/b5c3b2aa-0945-4ee8-9d17-0ffe388d3529/history
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
    "role": "user",
    "message": "Can you open excel files?",
    "extra_data": {}
}
```

##### Delete Chat

Deletes a specific chat and all its messages.

**Endpoint:** `DELETE /chats/{chat_id}`

**Headers:**

```
Authorization: Bearer {access_token}
```

**Example:**

```http
DELETE http://localhost:8010/api/v1/chats/b5c3b2aa-0945-4ee8-9d17-0ffe388d3529
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

##### Notes

- All authenticated routes require a valid JWT token obtained from the login endpoint.
- File uploads support multipart/form-data format.
- UUIDs are used as identifiers for chats and files.
- The `extra_data` field in chat messages can be used to pass additional structured information.

## License

No License

## Contributors

- Shakir Fattani - Project Lead
- Engineer's from Cambio-ML
