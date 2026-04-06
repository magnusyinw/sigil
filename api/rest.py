"""
Sigil REST API
Standard HTTP interface for all Sigil operations.
Interactive docs at /docs once server is running.
"""

import os
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.router import SigilRouter
from core.indexer import SigilIndexer


def create_api_app(router: SigilRouter, indexer: SigilIndexer) -> FastAPI:
    app = FastAPI(
        title="Sigil API",
        description=(
            "**Sigil** — Symbolic knowledge indexing for LLM systems.\n\n"
            "Every answer has an address.\n\n"
            "GitHub: [sigil-index/sigil](https://github.com/sigil-index/sigil)"
        ),
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Info ──────────────────────────────────────────────────────────

    @app.get("/", tags=["Info"])
    async def root():
        """Sigil API root — shows available endpoints."""
        stats = router.get_stats()
        return {
            "name":    "Sigil",
            "version": "1.0.0",
            "tagline": "Every answer has an address.",
            "stats":   stats,
            "endpoints": {
                "query":       "GET  /query?address=<address>",
                "list":        "GET  /list?prefix=<prefix>",
                "backlinks":   "GET  /backlinks?address=<address>",
                "skill_cards": "GET  /skill-cards",
                "conflicts":   "GET  /conflicts",
                "stats":       "GET  /stats",
                "index":       "POST /index  (multipart file upload)",
                "docs":        "GET  /docs",
            },
        }

    @app.get("/stats", tags=["Info"])
    async def stats():
        """Return index statistics."""
        return router.get_stats()

    # ── Query ─────────────────────────────────────────────────────────

    @app.get("/query", tags=["Query"])
    async def query(
        address: str = Query(..., description="Symbolic address, prefix, or natural language"),
    ):
        """
        Query the Sigil index.

        **Tier 1** (exact): `equipment.pump.fault.seal_leak.symptom`
        **Tier 2** (prefix): `equipment.pump`
        **Tier 3** (fuzzy): `vibration in centrifugal pump`
        """
        if not address:
            raise HTTPException(400, "address parameter is required")
        return router.query(address)

    @app.get("/list", tags=["Query"])
    async def list_addresses(
        prefix: str = Query("", description="Optional address prefix to filter"),
    ):
        """List all indexed symbolic addresses."""
        return router.list_addresses(prefix=prefix)

    @app.get("/backlinks", tags=["Query"])
    async def backlinks(
        address: str = Query(..., description="Symbolic address to find backlinks for"),
    ):
        """Find all knowledge nodes that link to a given address."""
        if not address:
            raise HTTPException(400, "address parameter is required")
        return router.get_backlinks(address)

    @app.get("/skill-cards", tags=["Query"])
    async def skill_cards():
        """List Skill Cards for all indexed documents."""
        return router.get_skill_cards()

    @app.get("/conflicts", tags=["Governance"])
    async def conflicts():
        """List conflict flags pending human review."""
        return router.get_conflicts()

    # ── Indexing ──────────────────────────────────────────────────────

    @app.post("/index", tags=["Indexing"])
    async def index_document(
        file:  UploadFile = File(..., description="Document to index (PDF, DOCX, MD, TXT, HTML)"),
        title: str        = Form("", description="Optional document title"),
    ):
        """
        Index a document file.

        Supported formats: PDF, DOCX, Markdown, TXT, HTML

        Returns the generated symbolic address index with Skill Card and audit results.
        """
        suffix = os.path.splitext(file.filename or "doc.txt")[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        try:
            result = indexer.index_file(tmp_path, title=title or file.filename)
            return {"status": "success", "filename": file.filename, **result}
        except Exception as e:
            raise HTTPException(500, str(e))
        finally:
            os.unlink(tmp_path)

    return app


def run(router: SigilRouter, indexer: SigilIndexer,
        host: str = "0.0.0.0", port: int = 3001):
    app = create_api_app(router, indexer)
    uvicorn.run(app, host=host, port=port, log_level="warning")
