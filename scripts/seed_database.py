"""Seed manual:  docker compose exec backend python -m app.seed   (atau python scripts/seed_database.py dari folder backend env)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.seed import seed_all

if __name__ == "__main__":
    seed_all()
    print("Seed selesai.")
