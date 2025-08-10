# <p align="center">Mockcruiter - Mock Interview Platform using AI Agents</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"></a>
  <a href="#"><img src="https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS"></a>
  <a href="#"><img src="https://img.shields.io/badge/Langchain-3498DB?style=for-the-badge" alt="Langchain"></a>
  <a href="#"><img src="https://img.shields.io/badge/Langgraph-0A0A0A?style=for-the-badge" alt="Langgraph"></a>
</p>

## Introduction

Mockcruiter is a platform designed to simulate job interviews. It allows users to upload their resume and practice answering interview questions generated dynamically based on their qualifications and the job requirements. The application utilizes real-time audio streaming and a sophisticated backend powered by Langchain and LLMs to create a realistic and interactive interview experience.

## Table of Contents

1.  [Key Features](#key-features)
2.  [Installation Guide](#installation-guide)
3.  [Usage](#usage)
4.  [Environment Variables](#environment-variables)
5.  [Project Structure](#project-structure)
6.  [Technologies Used](#technologies-used)
7.  [License](#license)

## Key Features

*   **Resume Upload:** Upload your resume (PDF) and provide job details (role, company, details).
*   **Dynamic Question Generation:** Questions are dynamically generated based on your resume and job specifications using Retrieval-Augmented Generation (RAG).
*   **Real-time Audio Streaming:** Simulate a real interview with real-time audio capture and playback using WebSockets.
*   **Speech-to-Text (STT):** Converts your spoken responses into text.
*   **Text-to-Speech (TTS):** Converts the interviewer's questions from text into synthesized speech.
*   **Interview Simulation:** Simulates interview flow of an interview with HR, Tech and Manager roles
*   **Comprehensive Interview Report:** Generates a detailed report summarizing your performance during the interview.

## Installation Guide

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install backend dependencies:**

    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3.  **Install frontend dependencies:**

    ```bash
    cd ../frontend
    npm install
    ```

4.  **Configure environment variables:**

    *   Create a `.env` file in the `backend` directory.
    *   Set the required environment variables (see [Environment Variables](#environment-variables) section).

5.  **Run the backend server:**

    ```bash
    cd ../backend
    python main.py
    ```

6.  **Run the frontend application:**

    ```bash
    cd ../frontend
    npm run dev
    ```

## Usage

1.  Open your web browser and navigate to the frontend application (usually `http://localhost:5173`).
2.  Upload your resume and provide the necessary job details on the upload page.
3.  The application will redirect you to the interview page.
4.  Allow microphone access when prompted.
5.  The interview will begin. Listen to the interviewer's questions and respond naturally.
6.  Once the interview is complete, you will be redirected to the report page to review your performance.

## Environment Variables

The following environment variables are required for the backend:

*   `GEMINI_API_KEY`: Google Gemini API key for the language model.
*   `DATABASE_URI`: The URI for the database (e.g., MongoDB connection string). *Not currently implemented, but reserved for future database integration.*
*   `WEBSOCKET_URL`: The websocket URL to connect to (e.g., `ws://localhost:8000/ws/`).

## Project Structure

```
├── backend/
│   ├── agent.py        # Defines interviewer nodes and interview flow
│   ├── main.py         # FastAPI application and websocket handling
│   ├── rag.py          # Implements Retrieval-Augmented Generation
│   ├── stt.py          # Speech-to-Text functionality
│   ├── tts.py          # Text-to-Speech functionality
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main application component and routing
│   │   ├── main.jsx        # Entry point for the React application
│   │   ├── index.css       # Global styles
│   │   ├── pages/
│   │   │   ├── home.jsx          # Interview Component
│   │   │   ├── interviewReport.jsx # Renders the interview report
│   │   │   └── uploadPage.jsx    # Resume upload page
│   ├── vite.config.js  # Vite configuration
│   ├── package.json    # Frontend dependencies
├── README.md       # This file
```

## Technologies Used

<p align="left">
    <a href="#"><img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI"></a>
    <a href="#"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
    <a href="#"><img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"></a>
    <a href="#"><img src="https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS"></a>
    <a href="#"><img src="https://img.shields.io/badge/Langchain-3498DB?style=for-the-badge" alt="Langchain"></a>
    <a href="#"><img src="https://img.shields.io/badge/Google_Gemini_AI-00857F?style=for-the-badge&labelColor=white" alt="Google Gemini AI"></a>
    <a href="#"><img src="https://img.shields.io/badge/WebSockets-4285F4?style=for-the-badge" alt="WebSockets"></a>
</p>

*   **Backend:** FastAPI, Python, Langchain, Google Gemini AI
*   **Frontend:** React, JavaScript, Tailwind CSS, Axios
*   **Other:** WebSockets

## License

MIT License
