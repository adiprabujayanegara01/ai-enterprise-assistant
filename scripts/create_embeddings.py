"""Index ulang seluruh dokumen (mis. setelah ganti model/dimensi embedding).
Docker: docker compose exec backend python -c "from app.services.document_service import reindex_all; print(reindex_all())" """
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.services.document_service import reindex_all

if __name__ == "__main__":
    print(f"{reindex_all()} dokumen diindeks ulang.")
