import sys
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Dict
from sqlalchemy.orm import Session
import ollama
import logging

from models import tables, engine, SessionLocal

#--- Logging Setup ---#
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/conversation.log'
)

router = APIRouter(
    prefix="/chat",
    tags="chat"
)

tables.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

active_connections: Dict[WebSocket, int] = {}

@router.websocket("/socket")
async def chat_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    conversatoin_id: int = -1
    
    try:
        new_conversation = tables.Conversation(title="New Chat Session")
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        
        conversation_id = new_conversation.conversation_id
        active_connections[websocket] = conversation_id
        logging.info(f"New WebSocket connected. Conversation ID: {conversation_id}")
        
        while True:
            # Receive user message
            data = await websocket.receive_text()
            
            # --- Save User Message ---
            user_message = tables.Message(
                conversation_id=conversation_id,
                author="user",
                description=data,
                title=data[:50]
            )
            db.add(user_message)
            db.commit()
            chat_history = db.query(tables.Message).filter(
                tables.Message.conversation_id == conversation_id
            ).order_by(tables.Message.message_id).all()

            ollama_messages = [{'role': msg.author, 'content': msg.description} for msg in chat_history]

            llm_response_content = ""
            try:
                response_generator = ollama.chat(
                    model='llama3.2',
                    messages=ollama_messages,
                    stream=True
                )
                for chunk in response_generator:
                    content = chunk['message']['content']
                    llm_response_content += content
                    await websocket.send_text(content) # Send chunks back to the client

            except ollama.ResponseError as e:
                logging.error(f"Ollama API error for conversation {conversation_id}: {e}")
                await websocket.send_text(f"Error from LLM: {e}")
                continue

            llm_message = tables.Message(
                conversation_id=conversation_id,
                author="assistant",
                description=llm_response_content,
                title="LLM Response" 
            )
            db.add(llm_message)
            
            db.commit()
            logging.info(f"Messages saved for conversation {conversation_id}")

    except WebSocketDisconnect:
        if websocket in active_connections:
            del active_connections[websocket]
        logging.info(f"Client disconnected. Conversation ID: {conversation_id}")
    except Exception as e:
        logging.error(f"An unhandled error occurred for conversation {conversation_id}: {e}", exc_info=True)
        try:
            await websocket.send_text("An internal server error occurred. Please try again.")
        except RuntimeError:
            logging.warning(f"Failed to send error message to disconnected client for conversation {conversation_id}")
        
        if websocket in active_connections:
            del active_connections[websocket]
