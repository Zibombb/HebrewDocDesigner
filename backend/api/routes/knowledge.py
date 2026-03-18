"""
knowledge.py - REST API for the Living Knowledge Atom Base.

GET  /api/knowledge/stats           - counts by type and status
GET  /api/knowledge/atoms           - list atoms (filter by type, status)
GET  /api/knowledge/atoms/search    - semantic search
GET  /api/knowledge/atoms/{id}      - single atom
GET  /api/knowledge/conflicts       - all CONFLICTED atoms
DELETE /api/knowledge/atoms/{id}    - delete atom
POST /api/knowledge/atoms/{id}/resolve - resolve a conflict (mark active)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.services import atom_store
from backend.models.schemas import KnowledgeAtomType

router = APIRouter()


@router.get("/knowledge/stats")
def get_stats():
    total = atom_store.get_atom_count()
    by_type = {}
    for t in KnowledgeAtomType:
        atoms = atom_store.get_all_atoms(atom_type=t.value)
        if atoms:
            by_type[t.value] = len(atoms)
    active = len(atom_store.get_all_atoms(status="active"))
    conflicted = len(atom_store.get_all_atoms(status="conflicted"))
    superseded = len(atom_store.get_all_atoms(status="superseded"))
    return {
        "total": total,
        "active": active,
        "conflicted": conflicted,
        "superseded": superseded,
        "by_type": by_type,
    }


@router.get("/knowledge/atoms/search")
def search_atoms(
    q: str = Query(..., description="Search query"),
    atom_type: Optional[str] = Query(None, description="Filter by atom type"),
    n: int = Query(10, description="Max results"),
):
    results = atom_store.search_atoms(query=q, atom_type=atom_type, n_results=n)
    return {"results": results, "count": len(results)}


@router.get("/knowledge/conflicts")
def get_conflicts():
    conflicts = atom_store.get_all_atoms(status="conflicted")
    return {"conflicts": conflicts, "count": len(conflicts)}


@router.get("/knowledge/atoms")
def get_atoms(
    atom_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    atoms = atom_store.get_all_atoms(atom_type=atom_type, status=status)
    return {"atoms": atoms, "count": len(atoms)}


@router.get("/knowledge/atoms/{atom_id}")
def get_atom(atom_id: str):
    atom = atom_store.get_atom_by_id(atom_id)
    if not atom:
        raise HTTPException(status_code=404, detail="Atom not found")
    return atom


@router.delete("/knowledge/atoms/{atom_id}")
def delete_atom(atom_id: str):
    atom = atom_store.get_atom_by_id(atom_id)
    if not atom:
        raise HTTPException(status_code=404, detail="Atom not found")
    atom_store.delete_atom(atom_id)
    return {"status": "deleted", "id": atom_id}


@router.post("/knowledge/atoms/{atom_id}/resolve")
def resolve_conflict(atom_id: str):
    """Mark a conflicted atom as active (human decision: this one is correct)."""
    from datetime import datetime
    atom = atom_store.get_atom_by_id(atom_id)
    if not atom:
        raise HTTPException(status_code=404, detail="Atom not found")
    if atom["status"] != "conflicted":
        raise HTTPException(status_code=400, detail="Atom is not in conflicted state")
    atom_store.update_atom_meta(
        atom_id,
        atom["content"],
        {"status": "active", "conflicts_with": "", "updated_at": datetime.now().isoformat()},
    )
    return {"status": "resolved", "id": atom_id}
