# OLED Inspection Runbook

## Prerequisites

- Google Cloud VM `oled-ubuntu-vm` running in project `oled-system`, zone `us-central1-f`.
- Docker and Docker Compose installed on the VM.
- Windows Python environment and camera available.
- SSH key authorized for the correct VM Linux user.

**Important:** The VM external IP can change after a stop/start. Replace `<VM_IP>` with the current IP. The Windows SSH user may be `INOSLAB`, while the project is under `/home/iakkar`; these are distinct Linux users with separate permissions.

## Check cloud services (Google Cloud Console SSH terminal)

```bash
cd /home/iakkar/oled-inspection-cloud
sudo docker compose ps
sudo docker logs --tail 100 oled-api
curl http://127.0.0.1:8000/api/health
```

To rebuild and start the API after a controlled change:

```bash
sudo docker compose up -d --build api
```

## Start SSH tunnel (Windows PowerShell)

```powershell
ssh -i "$env:USERPROFILE\.ssh\google_compute_engine" -N -o ExitOnForwardFailure=yes -L 8000:127.0.0.1:8000 INOSLAB@<VM_IP>
```

Leave this terminal open while accessing `http://localhost:8000/dashboard` from Windows. If a browser shows stale HTML, use Ctrl+Shift+R.

## Run Windows camera client

From the cloned repository:

```powershell
cd local
python -m pip install -r requirements.txt
python camera_inspection.py
```

Use an appropriate virtual environment and check the script's API URL. Do not assume it is configured automatically.

## Troubleshooting

- **SCP says `Permission denied (publickey)`:** Verify the SSH username and the key associated with it.
- **SCP says `Permission denied` for `/home/iakkar`:** SSH may succeed as `INOSLAB` without access to the other user's home directory. Copy source files to a permitted transfer directory using the VM console; avoid weakening home directory permissions.
- **SCP says `No such file or directory`:** Confirm the full path on the VM using `pwd` and `find`.
- **Dashboard unreachable:** Confirm VM running, API container healthy, SSH tunnel active, and port 8000 not occupied by another process.
- **No live updates:** Check `/api/events`, Redis container, and browser console; reload history if needed.
- **No JPEG preview:** Confirm the inspection image upload succeeded and check `GET /api/inspections/{id}/image`.

## Git workflow

```powershell
git status
git diff --cached --name-only
git commit -m "Update OLED inspection documentation"
git push origin main
```

Never stage VM runtime databases, JPEG images, SSH private keys, `.env` files, or backups. A Git push does **not** automatically update the running VM; CI currently only validates source syntax.
