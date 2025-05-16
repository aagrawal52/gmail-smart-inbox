from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any
import logging
from config.settings import MAX_RESULTS_PER_PAGE

logger = logging.getLogger(__name__)

class GmailClient:
    def __init__(self, credentials):
        """
        Initialize Gmail API client.
        
        Args:
            credentials: Google API credentials
        """
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def get_messages(self, label_ids: List[str] = ['INBOX']) -> List[Dict[str, Any]]:
        """
        Fetch messages with specified labels.
        
        Args:
            label_ids: List of label IDs to filter messages
            
        Returns:
            List of message IDs and metadata
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=MAX_RESULTS_PER_PAGE,
                labelIds=label_ids
            ).execute()
            
            message_list = results.get("messages", [])
            iter_num = 1
            
            while 'nextPageToken' in results:
                iter_num += 1
                results = self.service.users().messages().list(
                    userId='me',
                    maxResults=MAX_RESULTS_PER_PAGE,
                    pageToken=results['nextPageToken']
                ).execute()
                message_list.extend(results.get("messages", []))
            
            logger.info(f"Total Number of iterations = {iter_num}")
            logger.info(f"Total Number of mails fetched = {len(message_list)}")
            
            return message_list
            
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise
    
    def get_message_details(self, message_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific message.
        
        Args:
            message_id: ID of the message to fetch
            
        Returns:
            Message details
        """
        try:
            return self.service.users().messages().get(
                userId="me",
                id=message_id
            ).execute()
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """
        Get all labels for the user.
        
        Returns:
            List of label information
        """
        try:
            results = self.service.users().labels().list(userId='me').execute()
            return results.get('labels', [])
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise 