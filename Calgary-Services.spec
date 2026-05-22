# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Calgary Social Services
# Build: uv run pyinstaller Calgary-Services.spec --clean

a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("app/templates", "app/templates"),
        ("app/static", "app/static"),
    ],
    hiddenimports=[
        # uvicorn internals — not auto-discovered
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        # async backend
        "anyio",
        "anyio._backends._asyncio",
        "anyio.from_thread",
        # form / file upload parsing
        "multipart",
        "multipart.multipart",
        # misc
        "aiofiles",
        "jinja2",
        "h11",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "test", "unittest"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Calgary-Services",
    debug=False,
    strip=False,
    upx=True,
    console=True,   # keep console so users can see the URL + close to quit
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="Calgary-Services",
)
