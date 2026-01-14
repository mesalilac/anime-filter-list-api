import time
import httpx
import json

from app.models import (
    ShowModel,
    ShowResponseModel,
    ShowResponseCacheModel,
    ShowsListResponseCacheModel,
)
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.scrape import get_shows_list, get_show_by_slug
from contextlib import asynccontextmanager

API_DOCS_URL = "/docs"

with open("mal_mapping.json", "r", encoding="utf-8") as f:
    mal_to_slug_mapping: dict[str, str] = json.load(f)
    slug_to_mal_mapping: dict[str, int] = {
        v: int(k) for k, v in mal_to_slug_mapping.items()
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.httpx_client = httpx.AsyncClient()
    yield

    await app.state.httpx_client.aclose()


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=API_DOCS_URL)

router = APIRouter(prefix="/api/shows")

show_cache: dict[str, ShowResponseCacheModel] = {}
shows_list_cache: ShowsListResponseCacheModel | None = None

SHOW_CACHE_TTL = 43200  # 12 hours
SHOWS_LIST_CACHE_TTL = 259200  # 3 days


async def root():
    return RedirectResponse(url=API_DOCS_URL, status_code=301)


@app.get("/", include_in_schema=False)
@app.get("/api", include_in_schema=False)
@app.get("/api/docs", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url=API_DOCS_URL, status_code=301)


@router.get(
    "/",
    summary="Fetch all shows listed on animefillerlist.com",
    response_model=list[ShowModel],
)
async def get_shows():
    global shows_list_cache
    client: httpx.AsyncClient = app.state.httpx_client

    current_time = int(time.time())

    if (
        shows_list_cache is not None
        and current_time - shows_list_cache.last_updated_at < SHOWS_LIST_CACHE_TTL
    ):
        return shows_list_cache.data

    new_data = await get_shows_list(client, slug_to_mal_mapping)

    shows_list_cache = ShowsListResponseCacheModel(
        data=new_data, last_updated_at=current_time
    )

    return new_data


@router.get(
    "/{slug_or_id}",
    summary="Fetch a show using animefillerlist.com's slug or MAL ID",
    response_model=ShowResponseModel,
)
async def get_show(slug_or_id: str):
    client: httpx.AsyncClient = app.state.httpx_client

    current_time = int(time.time())

    if slug_or_id.isdigit():
        slug = mal_to_slug_mapping.get(slug_or_id)
        if not slug:
            raise HTTPException(status_code=404, detail="MAL ID not found in mapping")
    else:
        slug = slug_or_id

    cached_item = show_cache.get(slug)

    if cached_item and current_time - cached_item.last_updated_at < SHOW_CACHE_TTL:
        return cached_item.data

    new_data = await get_show_by_slug(client, slug, slug_to_mal_mapping)

    if new_data is None:
        raise HTTPException(status_code=404, detail="Show not found!")

    show_cache[slug] = ShowResponseCacheModel(
        data=new_data, last_updated_at=current_time
    )

    return new_data


app.include_router(router)
