import logging
import argparse
from src.auth import get_credentials
from src.gmail_client import GmailClient
from src.data_processor import DataProcessor
from utils.helpers import setup_logging, combine_csv_files
from config.settings import EMAILS_DIR

def parse_args():
    parser = argparse.ArgumentParser(description='Gmail Inbox Processing')
    parser.add_argument('--session-id', type=str, help='Custom session ID for processing')
    parser.add_argument('--fresh', action='store_true', help='Force fresh start even if checkpoint exists')
    return parser.parse_args()

def main():
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Get credentials
        credentials = get_credentials()
        
        # Initialize Gmail client
        gmail_client = GmailClient(credentials)
        
        # Fetch messages
        messages = gmail_client.get_messages()
        
        # Get and display labels
        labels = gmail_client.get_labels()
        label_mappings = {label['id']: label['name'] for label in labels}
        logger.info(f"Total labels found: {len(labels)}")
        
        # Process and save messages
        data_processor = DataProcessor(gmail_client)
        saved_file = data_processor.save_messages(
            messages, 
            label_mappings,
            session_id=args.session_id,
            force_new=args.fresh
        )
        logger.info(f"Messages saved to: {saved_file}")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 