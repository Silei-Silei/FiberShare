# Deployment

## Requirements

- A [Cloudflare](https://cloudflare.com) account (free)
- Python 3.8+ with `boto3` (`pip install boto3`)

## Steps

### 1. Create an R2 bucket

1. In the Cloudflare dashboard, go to **Storage & Databases > R2 Object Storage**.
2. Click **Create bucket**. Name it `fibershare-files` (or any name you prefer).
3. Note your **Account ID** shown on the R2 overview page.

### 2. Enable public access and configure CORS

1. Open the bucket → **Settings**.
2. Under **Public Access**, click **Allow Access**. Copy the public domain (e.g. `pub-xxx.r2.dev`).
3. Under **CORS Policy**, add:

```json
[
  {
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

### 3. Create an R2 API token

1. On the R2 overview page, click **Manage R2 API Tokens > Create API Token**.
2. Set permission to **Object Read & Write**, scope to your bucket.
3. Copy the **Access Key ID** and **Secret Access Key** (shown once).

### 4. Deploy the viewer

1. In the Cloudflare dashboard, go to **Compute > Workers & Pages**.
2. Click **Create > Upload your static files**.
3. Name the project `fibershare`, upload the `viewer/` folder.
4. Note the deployment URL (e.g. `https://fibershare.xxx.workers.dev`).

### 5. Configure credentials

Set environment variables (add to `~/.zshrc` or `~/.bashrc`):

```bash
export CF_ACCOUNT_ID="your_account_id"
export CF_ACCESS_KEY="your_access_key_id"
export CF_SECRET_KEY="your_secret_access_key"
export CF_BUCKET_NAME="fibershare-files"
export CF_R2_PUBLIC_URL="https://pub-xxx.r2.dev"
export FIBERSHARE_VIEWER_URL="https://fibershare.xxx.workers.dev"
```

### 6. Install the Python dependency

```bash
pip install boto3
```

You are now ready to use `upload.py`. See [README.md](README.md) for usage.
