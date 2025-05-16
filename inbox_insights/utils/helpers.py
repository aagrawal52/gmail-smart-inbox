import logging
from typing import Optional, List
import pandas as pd
from pathlib import Path

def setup_logging(log_level: int = logging.INFO) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level to use
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def combine_csv_files(file_paths: List[Path], output_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Combine multiple CSV files into one.
    
    Args:
        file_paths: List of paths to CSV files
        output_path: Optional path to save combined file
        
    Returns:
        Combined DataFrame
    """
    dfs = [pd.read_csv(f) for f in file_paths]
    combined_df = pd.concat(dfs, ignore_index=True)
    
    if output_path:
        combined_df.to_csv(output_path, index=False)
    
    return combined_df 