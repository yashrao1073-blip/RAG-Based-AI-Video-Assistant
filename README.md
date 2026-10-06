# RAG-Based-AI-Video-Assistant

AI Video Assistant is an intelligent application that converts YouTube videos and uploaded audio/video files into useful meeting insights. It generates a transcript, title, summary, action items, key decisions, and open questions using Artificial Intelligence.

The application also includes a RAG-based chat feature that allows users to ask questions about the analysed meeting or video and receive answers based on the transcript.

## Features

- Accepts YouTube URLs and local audio/video files.
- Extracts and processes audio from media files.
- Converts speech into text transcripts.
- Supports English and Hinglish transcription.
- Generates an AI-based title and summary.
- Extracts action items from discussions.
- Identifies key decisions and open questions.
- Provides downloadable transcripts.
- Includes a RAG-based chat system for asking questions about recordings.
- Offers a user-friendly Streamlit web interface.

## Technology Stack

- Python
- Streamlit
- Sarvam AI API
- yt-dlp
- Pydub
- FFmpeg
- LangChain
- Vector Database
- python-dotenv

## Project Structure

                    ┌─────────────────┐
                    │      User       │
                    └────────┬────────┘
                             │
              YouTube URL / Audio-Video File
                             │
                             ▼
                ┌──────────────────────┐
                │  Streamlit Interface │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   Input Processing   │
                │ Download / Upload    │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   Audio Processing   │
                │ Convert and Chunk    │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Speech-to-Text Module│
                │    Sarvam AI API     │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │      Transcript      │
                └───────┬────────┬─────┘
                        │        │
                        │        │
                        ▼        ▼
          ┌──────────────────┐  ┌─────────────────────┐
          │ AI Analysis      │  │ RAG / Vector Database│
          │ Module           │  └──────────┬──────────┘
          └────────┬─────────┘             │
                   │                       │
                   ▼                       ▼
      ┌────────────────────────┐  ┌─────────────────────┐
      │ Title                  │  │ Meeting Chat System │
      │ Summary                │  │ Question and Answer │
      │ Action Items           │  └──────────┬──────────┘
      │ Key Decisions          │             │
      │ Open Questions         │             │
      └───────────┬────────────┘             │
                  │                          │
                  └────────────┬─────────────┘
                               │
                               ▼
                 ┌────────────────────────┐
                 │ Results Displayed to   │
                 │ the User in Streamlit  │
                 └────────────────────────┘
