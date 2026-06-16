#!/usr/bin/env python3
"""
FiberShare uploader — uploads NIfTI and/or TCK files to Cloudflare R2
and prints a shareable viewer link.

Usage:
    python upload.py brain.nii.gz
    python upload.py brain.nii.gz tractography.tck
    python upload.py --volume brain.nii.gz --tract tractography.tck
"""

import argparse
import os
import sys
import hashlib
import mimetypes
from pathlib import Path
from urllib.parse import urlencode

import boto3
from botocore.config import Config

# ── Configuration ────────────────────────────────────────────────────────────
# Fill these in after creating your Cloudflare R2 bucket and API token.
# Or set them as environment variables (recommended).

CLOUDFLARE_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "")
CLOUDFLARE_ACCESS_KEY  = os.environ.get("CF_ACCESS_KEY",  "")
CLOUDFLARE_SECRET_KEY  = os.environ.get("CF_SECRET_KEY",  "")
BUCKET_NAME            = os.environ.get("CF_BUCKET_NAME", "fibershare-files")

# The public R2 domain (from bucket Settings → Public Access).
R2_PUBLIC_URL = os.environ.get("CF_R2_PUBLIC_URL", "")

# The public base URL of your Cloudflare Pages viewer deployment.
VIEWER_BASE_URL = os.environ.get("FIBERSHARE_VIEWER_URL", "")

# ─────────────────────────────────────────────────────────────────────────────


def get_r2_client():
    endpoint = f"https://{CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=CLOUDFLARE_ACCESS_KEY,
        aws_secret_access_key=CLOUDFLARE_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def file_hash(path: Path, length: int = 8) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:length]


def upload_file(client, local_path: Path, prefix: str = "") -> str:
    """Upload a file to R2 and return its public URL."""
    short_hash = file_hash(local_path)
    key = f"{prefix}{short_hash}/{local_path.name}"

    content_type, _ = mimetypes.guess_type(str(local_path))
    if content_type is None:
        content_type = "application/octet-stream"

    file_size = local_path.stat().st_size
    print(f"  Uploading {local_path.name} ({file_size / 1e6:.1f} MB)...", end=" ", flush=True)

    client.upload_file(
        str(local_path),
        BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type},
    )

    print("done")
    return f"{R2_PUBLIC_URL}/{key}"


def build_viewer_url(volume_url: str | None, tract_url: str | None, dti_v1_url: str | None = None) -> str:
    params = {}
    if volume_url:
        params["v"] = volume_url
    if tract_url:
        params["t"] = tract_url
    if dti_v1_url:
        params["d"] = dti_v1_url
    return f"{VIEWER_BASE_URL}?{urlencode(params)}"


def main():
    parser = argparse.ArgumentParser(description="Upload neuroimaging files to FiberShare")
    parser.add_argument("files", nargs="*", help="Files to upload (NIfTI and/or TCK)")
    parser.add_argument("--volume", "-v", help="NIfTI volume file (.nii, .nii.gz)")
    parser.add_argument("--tract",  "-t", help="Tractography file (.tck, .trk, ...)")
    parser.add_argument("--dti",    "-d", help="DTI V1 eigenvector NIfTI (4D, 3 volumes) for RGB direction encoding")
    args = parser.parse_args()

    # Resolve volume, tract, and dti from positional or named args
    volume_path = Path(args.volume) if args.volume else None
    tract_path  = Path(args.tract)  if args.tract  else None
    dti_path    = Path(args.dti)    if args.dti    else None

    for f in args.files:
        p = Path(f)
        name = p.name.lower()
        if name.endswith((".tck", ".trk", ".trx", ".vtk")):
            tract_path = p
        elif name.endswith((".nii.gz", ".nii", ".nrrd", ".mgh", ".mgz")):
            if volume_path is None:
                volume_path = p
            elif dti_path is None:
                dti_path = p

    if volume_path is None and tract_path is None and dti_path is None:
        parser.print_help()
        sys.exit(1)

    for p in filter(None, [volume_path, tract_path, dti_path]):
        if not p.exists():
            print(f"Error: file not found: {p}", file=sys.stderr)
            sys.exit(1)

    # Validate config
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_ACCESS_KEY or not CLOUDFLARE_SECRET_KEY:
        print(
            "Error: Cloudflare credentials not configured.\n"
            "Set CF_ACCOUNT_ID, CF_ACCESS_KEY, CF_SECRET_KEY, CF_BUCKET_NAME\n"
            "as environment variables, or edit upload.py directly.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = get_r2_client()

    volume_url  = upload_file(client, volume_path) if volume_path else None
    tract_url   = upload_file(client, tract_path)  if tract_path  else None
    dti_v1_url  = upload_file(client, dti_path)    if dti_path    else None

    viewer_url = build_viewer_url(volume_url, tract_url, dti_v1_url)

    print()
    print("Share this link:")
    print(viewer_url)
    print()

    # Copy to clipboard if possible
    try:
        import subprocess
        subprocess.run(["pbcopy"], input=viewer_url.encode(), check=True)
        print("(Copied to clipboard)")
    except Exception:
        pass


if __name__ == "__main__":
    main()
