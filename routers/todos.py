from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from database import Todo, get_session
from schemas import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/", response_model=list[TodoResponse])
async def get_todos(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Todo))
    return result.all()

@router.post("/", response_model=TodoResponse)
async def create_todo(todo: TodoCreate, session: AsyncSession = Depends(get_session)):
    db_todo = Todo(**todo.dict())
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int, 
    updated_data: TodoUpdate, 
    session: AsyncSession = Depends(get_session)
):
    db_todo = await session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db_todo.completed = updated_data.completed
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo

@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, session: AsyncSession = Depends(get_session)):
    db_todo = await session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    await session.delete(db_todo)
    await session.commit()
    return {"message": "Todo deleted"}