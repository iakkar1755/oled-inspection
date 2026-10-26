from datetime import datetime

from pathlib import Path
from fastapi.responses import FileResponse

import asyncio
import json
from fastapi.responses import StreamingResponse

from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Inspection


# Create database tables when the application starts.
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="OLED Inspection API",
    lifespan=lifespan
)

# Redis runs in a separate Docker container.
redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)


# Validate incoming inspection data.
class InspectionCreate(BaseModel):
    mean_brightness: float
    standard_deviation: float
    min_brightness: int
    max_brightness: int
    uniformity_score: float
    inspection_status: str


class InspectionResponse(InspectionCreate):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# Provide a database session for each request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "project": "OLED Inspection System",
        "backend": "FastAPI",
        "status": "running"
    }


@app.get("/api/health")
def health():
    try:
        redis_status = redis_client.ping()
        return {
            "api": "running",
            "redis": "connected" if redis_status else "disconnected"
        }
    except redis.RedisError:
        return {
            "api": "running",
            "redis": "disconnected"
        }


# Save an inspection result.
@app.post(
    "/api/inspections",
    response_model=InspectionResponse,
    status_code=201
)
def create_inspection(
    data: InspectionCreate,
    db: Session = Depends(get_db)
):
    inspection = Inspection(**data.model_dump())

    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    # Prepare the inspection event.
    event_data = InspectionResponse.model_validate(inspection).model_dump(mode="json")

    # Publish the event to Redis.
    try:
        redis_client.publish(
            "oled_inspections",
            json.dumps(event_data)
        )
    except redis.RedisError:
        pass

    return inspection


# Retrieve all inspection results.
@app.get(
    "/api/inspections",
    response_model=list[InspectionResponse]
)
def get_inspections(db: Session = Depends(get_db)):
    return db.scalars(
        select(Inspection).order_by(Inspection.id.desc())
    ).all()


# Retrieve one inspection by ID.
@app.get(
    "/api/inspections/{inspection_id}",
    response_model=InspectionResponse
)
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db)
):
    inspection = db.get(Inspection, inspection_id)

    if inspection is None:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    return inspection


@app.get("/api/events")
async def inspection_events():

    async def event_generator():
        client = redis.asyncio.Redis(
            host="redis",
            port=6379,
            decode_responses=True
        )

        pubsub = client.pubsub()

        try:
            await pubsub.subscribe("oled_inspections")

            # Confirm that the SSE connection is ready.
            yield ": connected\n\n"

            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0
                )

                if message and message["type"] == "message":
                    yield f"data: {message['data']}\n\n"

                await asyncio.sleep(0.1)

        finally:
            await pubsub.aclose()
            await client.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/dashboard")
def technician_dashboard():
    return FileResponse(
        Path(__file__).parent / "static" / "index.html"
    )


# Persistent directory for captured inspection images
IMAGE_DIR = Path("/app/data/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

MAX_IMAGE_SIZE = 5 * 1024 * 1024


@app.post("/api/inspections/{inspection_id}/image")
async def upload_inspection_image(
    inspection_id: int,
    image: UploadFile = File(...)
):
    # Verify that the inspection exists
    with SessionLocal() as db:
        inspection = db.get(Inspection, inspection_id)

        if inspection is None:
            raise HTTPException(
                status_code=404,
                detail="Inspection not found"
            )

    # Validate the uploaded image
    if image.content_type != "image/jpeg":
        raise HTTPException(
            status_code=415,
            detail="Only JPEG images are supported"
        )

    image_data = await image.read(MAX_IMAGE_SIZE + 1)

    if len(image_data) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image exceeds 5 MB limit"
        )

    if not image_data.startswith(b"\xff\xd8\xff"):
        raise HTTPException(
            status_code=400,
            detail="Invalid JPEG file"
        )

    image_path = IMAGE_DIR / f"inspection_{inspection_id}.jpg"
    image_path.write_bytes(image_data)

    return {
        "inspection_id": inspection_id,
        "image_url": f"/api/inspections/{inspection_id}/image",
        "message": "Image uploaded successfully"
    }


@app.get("/api/inspections/{inspection_id}/image")
def get_inspection_image(inspection_id: int):
    image_path = IMAGE_DIR / f"inspection_{inspection_id}.jpg"

    if not image_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )

    return FileResponse(
        image_path,
        media_type="image/jpeg"
    )
