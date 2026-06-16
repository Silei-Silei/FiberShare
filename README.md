# FiberShare

A browser-based viewer for neuroimaging data. Upload NIfTI volumes, TCK tractography files, and DTI orientation maps to Cloudflare R2, then share a single URL that anyone can open in a browser — no software installation required.

## Features

- Visualise NIfTI volumes (.nii, .nii.gz) with interactive axial, coronal, and sagittal views
- Overlay TCK/TRK tractography streamlines on anatomical volumes
- Display DTI V1 eigenvector maps as RGB direction-encoded overlays
- Share results via a single URL; recipients need only a browser

## Demo

**TCK tractography overlay:**
https://odd-dust-64a3.silei-zhu.workers.dev?v=https%3A%2F%2Fpub-fe063282402d4895ade32f83256cbda3.r2.dev%2F611f002a%2Fdti_FA.nii.gz&t=https%3A%2F%2Fpub-fe063282402d4895ade32f83256cbda3.r2.dev%2Fd30d09f1%2Fcst_l_clean.tck

**DTI orientation (V1 RGB) overlay:**
https://odd-dust-64a3.silei-zhu.workers.dev?v=https%3A%2F%2Fpub-fe063282402d4895ade32f83256cbda3.r2.dev%2Febc491b5%2FNMT_v2.0_sym_brain.nii.gz&d=https%3A%2F%2Fpub-fe063282402d4895ade32f83256cbda3.r2.dev%2F62af308d%2Fdyads1_moe_nmt.nii.gz

---

## Deployment

### 1. Cloudflare account

Sign up at [cloudflare.com](https://cloudflare.com) (free).

### 2. Create an R2 bucket

1. In the Cloudflare dashboard, go to **Storage & Databases > R2 Object Storage**.
2. Click **Create bucket**. Name it `fibershare-files` (or any name you prefer).
3. Note your **Account ID** shown on the R2 overview page.

### 3. Enable public access and configure CORS

1. Open the bucket, go to **Settings**.
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

### 4. Create an R2 API token

1. On the R2 overview page, click **Manage R2 API Tokens > Create API Token**.
2. Set permission to **Object Read & Write**, scope to your bucket.
3. Copy the **Access Key ID** and **Secret Access Key** (shown once).

### 5. Deploy the viewer

1. In the Cloudflare dashboard, go to **Compute > Workers & Pages**.
2. Click **Create > Upload your static files**.
3. Name the project `fibershare`, upload the `viewer/` folder.
4. Note the deployment URL (e.g. `https://fibershare.xxx.workers.dev`).

### 6. Configure credentials

Edit `upload.py` and fill in your values, or set environment variables:

```bash
export CF_ACCOUNT_ID="your_account_id"
export CF_ACCESS_KEY="your_access_key_id"
export CF_SECRET_KEY="your_secret_access_key"
export CF_BUCKET_NAME="fibershare-files"
export CF_R2_PUBLIC_URL="https://pub-xxx.r2.dev"
export FIBERSHARE_VIEWER_URL="https://fibershare.xxx.workers.dev"
```

### 7. Install the Python dependency

```bash
pip install boto3
```

---

## Usage

```bash
# Volume only
python3 upload.py brain.nii.gz

# Volume + tractography
python3 upload.py brain.nii.gz tractography.tck

# Volume + DTI V1 orientation
python3 upload.py brain.nii.gz --dti dti_V1.nii.gz

# Volume + tractography + DTI V1
python3 upload.py brain.nii.gz --dti dti_V1.nii.gz --tract tractography.tck
```

The script prints a shareable URL and copies it to the clipboard. Send the URL to collaborators; they open it in any modern browser.

## Embedding in a website

```html
<iframe
  src="https://fibershare.xxx.workers.dev/?v=FILE_URL"
  width="100%" height="500px"
  style="border: none;">
</iframe>
```

## File format requirements

| Parameter | Formats |
|---|---|
| `--volume` / `?v=` | .nii, .nii.gz, .nrrd, .mgh, .mgz |
| `--tract` / `?t=` | .tck, .trk, .trx, .vtk |
| `--dti` / `?d=` | .nii, .nii.gz (4D Float32, 3 volumes: x/y/z components of V1) |
