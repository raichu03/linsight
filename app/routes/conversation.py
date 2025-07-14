import sys
import os
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from typing import Dict
from sqlalchemy.orm import Session
import ollama
import logging

from models import tables, engine, SessionLocal
from utils import gen_query

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

with open('routes/tools.json', 'r', encoding='utf-8') as file:
    tool = json.load(file)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

active_connections: Dict[WebSocket, int] = {}

@router.websocket("/socket")
async def chat_endpoint(
    websocket: WebSocket, 
    db: Session = Depends(get_db),
    conversation_id: int | None = Query(None, alias="conversation_id")):
        
    await websocket.accept()
    current_conversation_id: int = -1
    user_message = []
    
    try:
        if conversation_id is None:
            await websocket.send_text("Please provide us with the conversation ID")
            if websocket in active_connections:
                del active_connections[websocket]
        
        else:
            existing_conversation = db.query(tables.Conversation).filter(
                tables.Conversation.conversation_id == conversation_id
            ).first()
            
            if existing_conversation:
                current_conversation_id = existing_conversation.conversation_id
                logging.info(f"Reconnecting to existing conversation ID: {current_conversation_id}")
                print(current_conversation_id)
                user_message = db.query(tables.Message).filter(
                    tables.Message.conversation_id == current_conversation_id
                ).order_by(tables.Message.message_id).all()
                
                await websocket.send_json({
                    "type": "history",
                    "messages": [{"author": msg.author, "content": msg.description} for msg in user_message]
                })
            
            else:
                print(conversation_id)
                logging.info(f"Conversation ID {conversation_id} not found. Starting new conversation.")
                new_conversation = tables.Conversation(
                    title="New Chat Session",
                    conversation_id=conversation_id
                )
                db.add(new_conversation)
                db.commit()
                db.refresh(new_conversation)
                current_conversation_id = new_conversation.conversation_id
                
                # Optionally send a message to the client indicating a new session
                await websocket.send_json({
                    "type": "new_session",
                    "conversation_id": current_conversation_id,
                    "message": "Starting a new chat session."
                })
                  
        active_connections[websocket] = conversation_id
        logging.info(f"New WebSocket connected. Conversation ID: {conversation_id}")
        
        while True:
            data = await websocket.receive_text()
            
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
                    tools=tool,
                )
                
                if response_generator ['message'].get('tool_calls'):
                    available_functions = {
                        "gen_query": gen_query,
                    }
                    
                    for tool_call in response_generator['message']['tool_calls']:
                        function_name = tool_call['function']['name']
                        function_args = tool_call['function']['arguments']
                        
                        if function_name == 'respond_directly':
                            print("this is not the tool call")
                            response = ollama.chat(
                                model='llama3.2',
                                messages=ollama_messages,
                                stream=True
                            )
                            
                            for chunk in response:
                                content = chunk['message']['content']
                                llm_response_content += content
                                await websocket.send_text(content)
                        
                        elif function_name == 'gen_query':
                            print("this is the tool call")
                            function_to_call = available_functions[function_name]
                            tool_output = function_to_call(**function_args)
                            await websocket.send_text(tool_output)
                            
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