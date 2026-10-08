import numpy as np
from app.services.embedding_service import hash_embed


def test_hash_embed_deterministic_and_normalized():
    a, b = hash_embed("prosedur reimbursement karyawan", 384), hash_embed("prosedur reimbursement karyawan", 384)
    assert a == b and abs(np.linalg.norm(a) - 1) < 1e-5


def test_hash_embed_similarity_ranks_related_higher():
    q = np.array(hash_embed("batas waktu pengajuan reimbursement", 384))
    rel = np.array(hash_embed("Pengajuan reimbursement paling lambat 14 hari", 384))
    unrel = np.array(hash_embed("banjir pantura keterlambatan pengiriman elektronik", 384))
    assert q @ rel > q @ unrel
