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

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for setup instructions.

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

The script prints a shareable URL and copies it to the clipboard.

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
