import json
from pathlib import Path
from typing import Set, Optional
import logging

logger = logging.getLogger(__name__)

class CheckpointManager:
    def __init__(self, checkpoint_dir: Path):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoint files
        """
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
    def save_checkpoint(self, session_id: str, processed_ids: Set[str]) -> None:
        """
        Save checkpoint of processed message IDs.
        
        Args:
            session_id: Unique identifier for the processing session
            processed_ids: Set of processed message IDs
        """
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{session_id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(list(processed_ids), f)
        logger.info(f"Checkpoint saved: {len(processed_ids)} messages")
    
    def load_checkpoint(self, session_id: str) -> Optional[Set[str]]:
        """
        Load checkpoint of processed message IDs.
        
        Args:
            session_id: Session identifier to load
            
        Returns:
            Set of processed message IDs if checkpoint exists, None otherwise
        """
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{session_id}.json"
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                processed_ids = set(json.load(f))
            logger.info(f"Checkpoint loaded: {len(processed_ids)} messages")
            return processed_ids
        return None
    
    def clear_checkpoint(self, session_id: str) -> None:
        """
        Clear checkpoint file.
        
        Args:
            session_id: Session identifier to clear
        """
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{session_id}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            logger.info(f"Checkpoint cleared: {session_id}")