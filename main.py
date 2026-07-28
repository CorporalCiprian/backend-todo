from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel
from database import SessionLocal, engine, Base
import os
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
import traceback

class TodoItem(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    completed = Column(Boolean, default=False)

class TodoCreate(BaseModel):
    title: str

class TodoUpdate(BaseModel):
    title: str
    completed: bool

class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool
    
    class Config:
        from_attributes = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"Database setup error: {e}")
    yield

app = FastAPI(title="Todo API")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error_type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc().splitlines()
        }
    )
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/todos/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoItem(title=todo.title)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/", response_model=list[TodoResponse])
def read_todos(db: Session = Depends(get_db)):
    return db.query(TodoItem).all()

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db_todo.title = todo.title
    db_todo.completed = todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return {"message": "Sters cu succes"}

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/test-db")
def test_database_connection():
    import socket
    import traceback
    from sqlalchemy import create_engine
    
    host = "todo-pg-server-123.postgres.database.azure.com" 
    port = 5432
    
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        network_status = "SUCCESS: Firewall is open and server is reachable."
    except Exception as e:
        return {"step": "Network Firewall Test", "error": str(e)}

    try:
        db_url = "postgresql://postgres:1q2w3e@todo-pg-server-123.postgres.database.azure.com:5432/todo_db?sslmode=require"
        
        engine = create_engine(db_url, connect_args={"connect_timeout": 5})
        
        with engine.connect() as connection:
            return {
                "step": "Database Login Test",
                "network": network_status,
                "status": "SUCCESS: We are logged into the database!"
            }
            
    except Exception as e:
        return {
            "step": "Database Login Test",
            "network": network_status,
            "error_type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc().splitlines()
        }