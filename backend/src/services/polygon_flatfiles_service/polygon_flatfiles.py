# backend/src/services/polygon_flatfiles_service/polygon_flatfiles.py

import os
import gzip
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
import boto3
from botocore.exceptions import ClientError

from core.config import PolygonFlatfileSettings

# Load settings
settings = PolygonFlatfileSettings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(">>> DEBUG ENV", dict(os.environ), flush=True)

# ----------------------------
# FastAPI App
# ----------------------------

app = FastAPI(
    title="Polygon Flat Files Service",
    description="Service to list, preview, and download Polygon S3 Flat Files",
    version="1.0.0"
)

# ----------------------------
# S3 Client
# ----------------------------

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.POLYGON_ACCESS_KEY_ID,
    aws_secret_access_key=settings.POLYGON_SECRET_ACCESS_KEY,
    endpoint_url=settings.POLYGON_S3_ENDPOINT,
)

# ----------------------------
# Endpoints
# ----------------------------

@app.get("/")
def root():
    return {"message": "Polygon Flat Files service is running."}


@app.get("/list-files")
def list_files(
    prefix: Optional[str] = Query(None, description="Prefix/path in the bucket, e.g., 'us_stocks_sip/day_aggs_v1/2024/03/'"),
    max_keys: int = 100
):
    """List objects in the S3 bucket under a given prefix."""
    try:
        logger.info(f"Listing files with prefix: {prefix}")
        kwargs = {
            "Bucket": settings.POLYGON_BUCKET_NAME,
            "MaxKeys": max_keys
        }
        if prefix:
            kwargs["Prefix"] = prefix

        response = s3_client.list_objects_v2(**kwargs)
        if "Contents" not in response:
            return {"message": "No objects found at that prefix."}

        objects = [
            {"Key": obj["Key"], "Size": obj["Size"], "LastModified": str(obj["LastModified"])}
            for obj in response["Contents"]
        ]

        return {"bucket": settings.POLYGON_BUCKET_NAME, "prefix": prefix or "", "objects": objects}
    except ClientError as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/preview-file")
def preview_file(key: str, lines: int = 5):
    """Download a file (gzipped or plain) and return the first N lines."""
    try:
        logger.info(f"Previewing file: {key}")
        obj = s3_client.get_object(Bucket=settings.POLYGON_BUCKET_NAME, Key=key)
        data = obj["Body"].read()

        if key.endswith(".gz"):
            data = gzip.decompress(data)

        text = data.decode("utf-8", errors="ignore")
        all_lines = text.splitlines()

        return {"file_key": key, "preview_lines": all_lines[:lines]}
    except ClientError as e:
        logger.error(f"Error previewing file: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/download-file")
def download_file(key: str):
    """Download an entire file from S3."""
    try:
        logger.info(f"Downloading file: {key}")
        obj = s3_client.get_object(Bucket=settings.POLYGON_BUCKET_NAME, Key=key)
        data = obj["Body"].read()

        if key.endswith(".gz"):
            return {"file_key": key, "size": len(data), "content": "gzipped_data_returned"}
        else:
            text = data.decode("utf-8", errors="ignore")
            return {"file_key": key, "size": len(data), "content": text}
    except ClientError as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=400, detail=str(e))
