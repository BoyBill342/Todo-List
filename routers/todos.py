from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from core.dependencies import get_current_user
from database import Todo, get_session, User
from schemas import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/", response_model=list[TodoResponse])
async def get_todos(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await session.exec(
        select(Todo).where(Todo.user_id == current_user.id)    
    )
    return result.all()

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: TodoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Associate todo with current user
    db_todo = Todo(**todo.dict(), user_id=current_user.id)
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int, 
    updated_data: TodoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_todo = await session.get(Todo, todo_id)
    
    # Check todo exists and belongs to user
    if not db_todo or db_todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    # Update todo data
    todo_data = updated_data.dict(exclude_unset=True)
    for key, value in todo_data.items():
        setattr(db_todo, key, value)
    
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo

@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_todo = await session.get(Todo, todo_id)
    
    # Verify ownership before deletion
    if not db_todo or db_todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    await session.delete(db_todo)
    await session.commit()
    return {"message": "Todo deleted successfully"}