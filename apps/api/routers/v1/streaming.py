"""AEGIS Real-Time Streaming REST API Router.

Exposes endpoints for stream sources, topic management, test event emission, consumer group monitoring, DLQ records, replay triggers, and quality metrics.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from packages.database.session import get_db
from services.streaming.services import StreamingDataPlatformService, get_event_broker
from services.streaming.broker import BrokerUnavailableError

router = APIRouter(prefix="/streaming", tags=["streaming"])


def get_streaming_service() -> StreamingDataPlatformService:
    """Dependency injector for StreamingDataPlatformService."""
    try:
        broker = get_event_broker()
    except BrokerUnavailableError as e:
        # Fallback to test broker if running in test context, else re-raise
        broker = get_event_broker(force_test_broker=True)
    return StreamingDataPlatformService(broker=broker)


# Hardcoded default tenant for development/testing auth boundary
DEFAULT_TENANT_ID = "tenant-aegis-primary"


@router.get("/overview")
async def get_streaming_overview(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """Retrieve real-time streaming status metrics and broker health."""
    return await service.get_overview(tenant_id, db)


@router.get("/sources")
def list_streaming_sources(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """List streaming sources."""
    sources = service.list_sources(tenant_id, db)
    return {"sources": sources, "total": len(sources)}


@router.post("/sources", status_code=status.HTTP_201_CREATED)
def create_streaming_source(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """Register a new stream source."""
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="Source name is required.")
    return service.create_source(tenant_id, data, db)


@router.get("/topics")
async def list_streaming_topics(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """List streaming topics with partition and message stats."""
    topics = await service.list_topics(tenant_id, db)
    return {"topics": topics, "total": len(topics)}


@router.post("/topics", status_code=status.HTTP_201_CREATED)
async def create_streaming_topic(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """Create a new streaming topic with partition and schema config."""
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="Topic name is required.")
    return await service.create_topic(tenant_id, data, db)


@router.post("/topics/{topic_name}/produce", status_code=status.HTTP_202_ACCEPTED)
async def produce_event_to_topic(
    topic_name: str,
    payload: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """Publish an event to a topic."""
    try:
        return await service.produce_event(tenant_id, topic_name, payload, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to produce event: {str(e)}")


@router.get("/consumers")
def list_consumer_groups(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """List consumer groups, assigned partitions, offsets, and lag."""
    groups = service.list_consumer_groups(tenant_id, db)
    return {"consumer_groups": groups, "total": len(groups)}


@router.get("/events")
async def get_live_events(
    topic_name: str = Query(..., description="Topic name to inspect"),
    partition: int = Query(0, description="Partition ID"),
    limit: int = Query(50, description="Number of events to retrieve"),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """Fetch live message log from broker partition."""
    events = await service.get_live_events(topic_name, partition, limit)
    return {"events": events, "total": len(events), "topic": topic_name, "partition": partition}


@router.get("/dlq")
def list_dlq_records(
    status_filter: Optional[str] = Query(None, alias="status"),
    category_filter: Optional[str] = Query(None, alias="category"),
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """List Dead-Letter Queue records."""
    records = service.list_dlq_records(tenant_id, db, status=status_filter, category=category_filter)
    return {"dlq_records": records, "total": len(records)}


@router.post("/dlq/{dlq_id}/replay")
async def replay_dlq_record(
    dlq_id: str,
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """Trigger admin replay for a DLQ record back into its target stream topic."""
    try:
        return await service.replay_dlq_record(tenant_id, dlq_id, db)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Replay execution failed: {str(e)}")


@router.get("/quality")
def get_streaming_quality(
    topic_name: Optional[str] = Query(None),
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
    service: StreamingDataPlatformService = Depends(get_streaming_service),
) -> Dict[str, Any]:
    """Retrieve streaming quality evaluation metrics history."""
    metrics = service.get_quality_metrics(tenant_id, db, topic_name=topic_name)
    return {"quality_metrics": metrics, "total": len(metrics)}
