import pandas as pd
from datetime import datetime
import os
from typing import List, Dict, Any, Set, Optional
import logging
from config.settings import EMAILS_DIR, DUMP_FREQUENCY
from tqdm import tqdm
import ast
import base64
from bs4 import BeautifulSoup
import numpy as np
from pathlib import Path
from .email_parser import EmailParser
from .checkpoint_manager import CheckpointManager


logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, gmail_client, checkpoint_dir: Optional[Path] = None):
        """Initialize data processor with necessary directories."""
        if not EMAILS_DIR.exists():
            logger.info(f"Creating directory: {EMAILS_DIR}")
            EMAILS_DIR.mkdir(parents=True, exist_ok=True)
            
        self.gmail_client = gmail_client
        self.email_parser = EmailParser()
        self.checkpoint_manager = CheckpointManager(
            checkpoint_dir or EMAILS_DIR / "checkpoints"
        )
    
    def _get_header(self, message: Dict[str, Any], header_name: str) -> str:
        """Extract header value from message headers."""
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == header_name.lower():
                return header['value']
        return ''
    
    def save_messages(self, messages: List[Dict[str, Any]], 
                     label_mappings: Dict[str, str],
                     session_id: Optional[str] = None,
                     force_new: bool = False) -> str:
        """
        Save messages to CSV file with timestamps and resume support.
        
        Args:
            messages: List of message data to save
            label_mappings: Dictionary mapping label IDs to label names
            session_id: Optional custom session identifier
            force_new: If True, starts a fresh process even if checkpoint exists
            
        Returns:
            Path to the saved file
        """
        # Use custom session_id if provided, otherwise use timestamp
        start_time = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        session_id = session_id or start_time
        file_path = EMAILS_DIR / f"email_{session_id}.csv"
        
        # Check for existing checkpoint
        existing_checkpoint = self.checkpoint_manager.load_checkpoint(session_id)
        if existing_checkpoint and not force_new:
            logger.info(f"Found existing checkpoint for session {session_id}")
            if input("Resume existing session? (y/n): ").lower() != 'y':
                force_new = True
        
        # Handle fresh start with existing session_id
        if force_new:
            logger.info(f"Starting fresh process with session ID: {session_id}")
            self.checkpoint_manager.clear_checkpoint(session_id)
            if file_path.exists():
                file_path.unlink()  # Remove existing file
            processed_ids = set()
        else:
            processed_ids = existing_checkpoint or set()
        
        # Filter out already processed messages
        remaining_messages = [
            msg for msg in messages 
            if msg['id'] not in processed_ids
        ]
        
        if processed_ids:
            logger.info(f"Resuming processing: {len(remaining_messages)} messages remaining")
        
        message_response = []
        try:
            # Add progress bar
            for i, message in tqdm(enumerate(remaining_messages), 
                                 total=len(remaining_messages),
                                 desc="Processing emails"):
                # Get full message details
                message_details = self.gmail_client.get_message_details(message['id'])
                
                # Parse email body
                body = self.email_parser.parse_with_error_handling(
                    message_details.get('payload', {})
                )
                
                # Convert label IDs to names
                label_ids = message_details.get('labelIds', [])
                labels = [label_mappings.get(label_id, label_id) for label_id in label_ids]
                
                # Create processed message
                processed_message = {
                    **message_details,
                    'body': body,
                    'labels': labels
                }
                
                if (i % DUMP_FREQUENCY == 0) and (i != 0):
                    # Write batch to file
                    mode = 'w' if i == DUMP_FREQUENCY and not processed_ids else 'a'
                    header = i == DUMP_FREQUENCY and not processed_ids
                    
                    pd.DataFrame(message_response).to_csv(
                        file_path,
                        header=header,
                        index=False,
                        mode=mode
                    )
                    
                    # Update checkpoint
                    processed_ids.update(msg['id'] for msg in message_response)
                    self.checkpoint_manager.save_checkpoint(session_id, processed_ids)
                    
                    message_response = []
                
                message_response.append(processed_message)
            
            # Write remaining messages
            if message_response:
                pd.DataFrame(message_response).to_csv(
                    file_path,
                    header=not file_path.exists(),
                    index=False,
                    mode='a'
                )
                
                # Final checkpoint update
                processed_ids.update(msg['id'] for msg in message_response)
                self.checkpoint_manager.save_checkpoint(session_id, processed_ids)
            
            # Rename file with end timestamp
            end_time = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            final_path = EMAILS_DIR / f"email_{session_id}_{end_time}.csv"
            os.rename(file_path, final_path)
            
            # Clear checkpoint after successful completion
            self.checkpoint_manager.clear_checkpoint(session_id)
            
            return str(final_path)
            
        except Exception as e:
            logger.error(f"Error during processing: {e}")
            # Save checkpoint before raising exception
            if message_response:
                processed_ids.update(msg['id'] for msg in message_response)
                self.checkpoint_manager.save_checkpoint(session_id, processed_ids)
            raise

# def base64url_decode(data):
#     """Decode base64url-encoded data."""
#     data = data.encode('utf-8')
#     data += b'=' * (4 - (len(data) % 4))
#     return base64.urlsafe_b64decode(data)

# def is_html_text(text):
#     """Check if text contains HTML."""
#     try:
#         soup = BeautifulSoup(text, 'html.parser')
#         return len(soup.find_all()) > 0
#     except:
#         return False

# def find_text_part(parts):
#     """Extract text from message parts."""
#     res_string = ""
#     for part in parts:
#         mimeType = part.get('mimeType')
#         if mimeType == 'text/plain':
#             data = part.get('body', {}).get('data')
#             if data:
#                 text = base64url_decode(data).decode('utf-8')
#                 if is_html_text(text):
#                     soup = BeautifulSoup(text, 'html.parser')
#                     res_string = res_string + " " + soup.get_text(separator=' ')
#                 else:
#                     res_string = res_string + " " + text           
#         elif mimeType == 'text/html':
#             data = part.get('body', {}).get('data')
#             if data:
#                 html = base64url_decode(data).decode('utf-8')
#                 soup = BeautifulSoup(html, 'html.parser')
#                 res_string = res_string + " " + soup.get_text(separator=' ')
#         elif mimeType in ['multipart/alternative', 'multipart/related']:
#             res_string = res_string + " " + find_text_part(part.get('parts', []))
#     return res_string

# def parse_email_body(payload):
#     """Parse email body from payload."""
#     if payload['mimeType'] == 'text/plain':
#         data = payload.get('body', {}).get('data')
#         if data:
#             return base64url_decode(data).decode('utf-8')
#     elif payload['mimeType'] == 'text/html':
#         data = payload.get('body', {}).get('data')
#         if data:
#             html = base64url_decode(data).decode('utf-8')
#             soup = BeautifulSoup(html, 'html.parser')
#             return soup.get_text(separator=' ')
#     elif payload['mimeType'].startswith('multipart/'):
#         parts = payload.get('parts', [])
#         text = find_text_part(parts)
#         if text:
#             return text
#     return ""

# def parse_text(x):
#     """Clean and normalize text."""
#     y = ''.join([i if ord(i) < 128 else ' ' for i in x])
#     return ' '.join(y.strip().split())

# def parse_email_body_with_try(payload):
#     """Safely parse email body with error handling."""
#     try:
#         x = parse_text(parse_email_body(payload))
#         return x
#     except:
#         return "Unable to Parse"