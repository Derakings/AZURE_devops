"""
Task management routes
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.database import get_db
from app.core.cache import cache_get, cache_set, cache_delete, cache_delete_pattern
from app.models.models import Task, User, TaskStatus, TaskPriority
from app.schemas.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    PaginatedResponse,
    MessageResponse
)
from app.api.dependencies import get_current_active_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task"""
    new_task = Task(
        **task_data.model_dump(),
        owner_id=current_user.id
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    # Invalidate cache
    await cache_delete_pattern(f"tasks:user:{current_user.id}:*")
    
    return new_task


@router.get("", response_model=PaginatedResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List tasks with pagination and filters"""
    # Build cache key
    cache_key = f"tasks:user:{current_user.id}:page:{page}:size:{page_size}:status:{status}:priority:{priority}:search:{search}"
    
    # Try cache first
    cached_data = await cache_get(cache_key)
    if cached_data:
        return cached_data
    
    # Build query
    query = select(Task).where(Task.owner_id == current_user.id)
    
    if status:
        query = query.where(Task.status == status)
    
    if priority:
        query = query.where(Task.priority == priority)
    
    if search:
        query = query.where(
            or_(
                Task.title.ilike(f"%{search}%"),
                Task.description.ilike(f"%{search}%")
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Task.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Prepare response
    response_data = {
        "items": [TaskResponse.model_validate(task) for task in tasks],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
    
    # Cache the result
    await cache_set(cache_key, response_data)
    
    return response_data


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific task"""
    # Try cache first
    cache_key = f"task:{task_id}"
    cached_task = await cache_get(cache_key)
    if cached_task:
        return cached_task
    
    result = await db.execute(
        select(Task).where(
            and_(Task.id == task_id, Task.owner_id == current_user.id)
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Cache the task
    task_data = TaskResponse.model_validate(task)
    await cache_set(cache_key, task_data.model_dump())
    
    return task_data


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a task"""
    result = await db.execute(
        select(Task).where(
            and_(Task.id == task_id, Task.owner_id == current_user.id)
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    
    # Mark as completed if status changed to completed
    if update_data.get("status") == TaskStatus.COMPLETED and task.status != TaskStatus.COMPLETED:
        update_data["completed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    # Invalidate caches
    await cache_delete(f"task:{task_id}")
    await cache_delete_pattern(f"tasks:user:{current_user.id}:*")
    
    return task


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a task"""
    result = await db.execute(
        select(Task).where(
            and_(Task.id == task_id, Task.owner_id == current_user.id)
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    await db.delete(task)
    await db.commit()
    
    # Invalidate caches
    await cache_delete(f"task:{task_id}")
    await cache_delete_pattern(f"tasks:user:{current_user.id}:*")
    
    return {"message": "Task deleted successfully"}


@router.get("/stats/summary")
async def get_task_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get task statistics for current user"""
    cache_key = f"stats:user:{current_user.id}"
    cached_stats = await cache_get(cache_key)
    if cached_stats:
        return cached_stats
    
    # Count tasks by status
    status_counts = {}
    for task_status in TaskStatus:
        result = await db.execute(
            select(func.count()).where(
                and_(Task.owner_id == current_user.id, Task.status == task_status)
            )
        )
        status_counts[task_status.value] = result.scalar()
    
    # Count tasks by priority
    priority_counts = {}
    for task_priority in TaskPriority:
        result = await db.execute(
            select(func.count()).where(
                and_(Task.owner_id == current_user.id, Task.priority == task_priority)
            )
        )
        priority_counts[task_priority.value] = result.scalar()
    
    stats = {
        "total_tasks": sum(status_counts.values()),
        "by_status": status_counts,
        "by_priority": priority_counts
    }
    
    # Cache stats
    await cache_set(cache_key, stats, ttl=60)  # Cache for 1 minute
    
    return stats
