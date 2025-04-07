# backend/src/util/logging_config.py

import logging

def configure_logging():
    # Reduce noise from libraries
    logging.getLogger('botocore').setLevel(logging.INFO)
    logging.getLogger('boto3').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)

    # Set up root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Log once (not recursively)
    logging.info("Logging configured successfully.")
