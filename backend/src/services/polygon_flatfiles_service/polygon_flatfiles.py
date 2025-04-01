# backend/app/microservices/polygon_flatfiles_service/polygon_flatfiles.py

import os
import gzip
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

##############################
# Load environment variables #
##############################

# If your .env is at backend/.env, we can load it here:
ENV_PATH = os.path.join(os.path.dirname(__file__), "../../../../.env")
load_dotenv(ENV_PATH)

# Read needed environment variables
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
S3_ACCESS_KEY = os.getenv("POLYGON_ACCESS_KEY_ID", "")
S3_SECRET_KEY = os.getenv("POLYGON_SECRET_ACCESS_KEY", "")
S3_ENDPOINT = os.getenv("POLYGON_S3_ENDPOINT", "https://files.polygon.io")
S3_BUCKET = os.getenv("POLYGON_BUCKET_NAME", "flatfiles")

##############################
# Create the microservice    #
##############################

app = FastAPI(
    title="Polygon Flat Files Microservice",
    description="Microservice to list, preview, and download Polygon S3 Flat Files",
    version="1.0.0"
)

# Create a Boto3 S3 client pointing to Polygon’s endpoint
s3_client = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    endpoint_url=S3_ENDPOINT,
)

@app.get("/")
def root():
    return {"message": "Polygon Flat Files microservice running."}


@app.get("/list-files")
def list_files(
    prefix: Optional[str] = Query(None, description="Prefix/path in the bucket, e.g. 'us_stocks_sip/day_aggs_v1/2024/03/'"),
    max_keys: int = 100
):
    """
    Lists objects in the S3 bucket under a given prefix.
    Similar to 'mc ls s3polygon/flatfiles/prefix'
    """
    try:
        kwargs = {
            "Bucket": S3_BUCKET,
            "MaxKeys": max_keys
        }
        if prefix:
            kwargs["Prefix"] = prefix

        response = s3_client.list_objects_v2(**kwargs)
        if "Contents" not in response:
            return {"message": "No objects found at that prefix."}

        objects = []
        for obj in response["Contents"]:
            objects.append({
                "Key": obj["Key"],
                "Size": obj["Size"],
                "LastModified": str(obj["LastModified"])
            })

        return {
            "bucket": S3_BUCKET,
            "prefix": prefix if prefix else "",
            "objects": objects
        }
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/preview-file")
def preview_file(key: str, lines: int = 5):
    """
    Downloads the file (gz or not) and returns the first N lines.
    """
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        data = obj["Body"].read()

        # Decompress if .gz
        if key.endswith(".gz"):
            data = gzip.decompress(data)

        text = data.decode("utf-8", errors="ignore")
        all_lines = text.splitlines()

        return {
            "file_key": key,
            "preview_lines": all_lines[:lines]
        }
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download-file")
def download_file(key: str):
    """
    Downloads an entire file from S3. 
    Returns the contents as text if not gzipped, or a note if gzipped.
    For large files, consider streaming or local storing.
    """
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        data = obj["Body"].read()

        if key.endswith(".gz"):
            # Optionally decompress, or return raw bytes
            return {
                "file_key": key,
                "size": len(data),
                "content": "gzipped_data_returned"
            }
        else:
            text = data.decode("utf-8", errors="ignore")
            return {
                "file_key": key,
                "size": len(data),
                "content": text
            }
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))
