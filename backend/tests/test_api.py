"""
Contract tests — verify the API shape matches the frontend types.
Run: pytest tests/test_api.py
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.database import Base, get_db


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def test_db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield session_factory
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(test_db):
    async def override_db():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.anyio
async def test_queue_empty(client):
    resp = await client.get("/api/v1/queue")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.anyio
async def test_item_not_found(client):
    resp = await client.get("/api/v1/items/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_draft_not_found(client):
    resp = await client.get("/api/v1/drafts/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_matters_empty(client):
    resp = await client.get("/api/v1/matters")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.anyio
async def test_draft_isolation():
    """
    Assert that no code path in ingestion/scoring/scheduling touches the draft service.
    This is a static import check — the draft service must only be imported from items.py.
    """
    import ast
    import pathlib

    draft_service_imports = []
    backend_src = pathlib.Path(__file__).parent.parent / "app"

    for py_file in backend_src.rglob("*.py"):
        if "draft_service" in py_file.name:
            continue
        try:
            tree = ast.parse(py_file.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module and "draft_service" in node.module:
                    draft_service_imports.append(str(py_file))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if "draft_service" in alias.name:
                            draft_service_imports.append(str(py_file))

    allowed = ["items.py"]
    violations = [f for f in draft_service_imports if not any(a in f for a in allowed)]
    assert violations == [], f"Draft service imported outside of allowed paths: {violations}"
