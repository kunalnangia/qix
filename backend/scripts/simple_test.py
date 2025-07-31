import os
import sys
import logging
from pathlib import Path

# Set up logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='simple_test.log',
    filemode='w'  # Overwrite existing log file
)

# Also log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting simple test script")
    
    # Get current working directory
    cwd = os.getcwd()
    logger.info(f"Current working directory: {cwd}")
    
    # List files in current directory
    try:
        files = os.listdir()
        logger.info("Files in current directory:")
        for f in files:
            logger.info(f"- {f}")
    except Exception as e:
        logger.error(f"Error listing directory: {e}")
    
    # Test file writing
    test_file = "test_output.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("This is a test file. If you see this, file writing works!")
        logger.info(f"Successfully wrote to {test_file}")
    except Exception as e:
        logger.error(f"Error writing to file: {e}")
    
    logger.info("Simple test completed")

if __name__ == "__main__":
    main()
