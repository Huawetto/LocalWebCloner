#!/usr/bin/env python3
"""
crawl.py
========
Entry-point compatibile col vecchio nome. Delega a sitecloner.__main__.

Uso rapido:
    python crawl.py https://example.com
    python crawl.py https://example.com -o ./mirror --depth 5 --workers 32

Uso interattivo (nessun argomento):
    python crawl.py
"""

from sitecloner.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
