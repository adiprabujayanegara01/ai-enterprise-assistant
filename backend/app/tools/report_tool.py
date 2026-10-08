import os
import re
import uuid
from datetime import datetime

from app.core.config import settings


def generate_report(ctx, title: str, content: str):
    os.makedirs(settings.reports_dir, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40] or "laporan"
    name = f"{slug}-{uuid.uuid4().hex[:6]}.md"
    body = f"# {title}\n\n_Dibuat {datetime.now():%Y-%m-%d %H:%M} oleh AI Enterprise Assistant_\n\n{content}\n"
    with open(os.path.join(settings.reports_dir, name), "w", encoding="utf-8") as f:
        f.write(body)
    return {"filename": name, "download_url": f"/api/agent/reports/{name}"}
