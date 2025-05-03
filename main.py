from datetime import datetime
import json
from typing import Dict, List
from fastapi import FastAPI, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, crud, auth, schemas
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from schemas import EmployeeSimple, Skill, ContactInfo, EmployeeCreate
from models import Employee, User, Task, TaskStatus
from auth import get_current_user
from granite_api_client import granite_result

app = FastAPI()

# Allow origins
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- allow these frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # <-- allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # <-- allow all headers
)
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return pwd_context.hash(password)


@app.post("/signup")
def signup(request: schemas.SignupRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, request.username)
    if not user:
        hashed_password = get_password_hash(request.password)
        user_create_data = schemas.UserCreate(
            username=request.username,
            password_hash=hashed_password,
            role=request.role,
        )
        crud.create_user(user_create_data, db)
        access_token = auth.create_access_token(
            data={"sub": request.username, "role": request.role}
        )
        new_user = crud.get_user_by_username(db, request.username)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "message": "User created successfully",
            "id": new_user.id,
            "username": request.username,
            "role": request.role,
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="Username already taken",
        )


# Login route
@app.post("/login")
def login(
    request: schemas.SignupRequest,
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_username(db, request.username)
    if not user or not crud.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }


@app.post("/employee")
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = db.query(User).filter(User.username == current_user["username"]).first()

    if not user or user.role != "employee":
        raise HTTPException(status_code=404, detail="Employee not found or not valid")

    new_employee = Employee(
        user_id=user.id,
        description=data.bio,
        skills=json.dumps([skill.dict() for skill in data.skills]),
        email=data.contactInfo.email,
        phone=data.contactInfo.phone,
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return {"message": "Employee profile created", "employee_id": data}


@app.get("/employee/{id}")
def getEmployee(id: int, db: Session = Depends(get_db)):
    return crud.get_employee_by_id(id, db)


@app.get("/employees/details")
def getEmployeesDetail(db: Session = Depends(get_db)):
    return crud.get_employees(db)


@app.get("/task/{id}")
def getTaskById(id: int, db: Session = Depends(get_db)):
    return crud.get_task_by_id(id, db)


@app.put("/task/{task_id}/complete")
def mark_task_completed(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user = crud.get_user_by_username(db, current_user["username"])

    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.accepted_by == current_user.id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404, detail="Task not found or you don't have permission"
        )

    if task.status != TaskStatus.in_progress:
        raise HTTPException(
            status_code=400, detail="Only tasks in progress can be marked as completed"
        )

    # Determine completion status
    current_time = datetime.now()
    is_late = task.deadline and current_time > task.deadline

    task.status = (
        TaskStatus.completed_after_deadline
        if is_late
        else TaskStatus.completed_before_deadline
    )
    task.completed_at = current_time

    db.commit()
    db.refresh(task)

    return {
        "message": "Task marked as completed",
        "status": task.status,
        "completed_at": task.completed_at,
        "was_late": is_late,
    }


@app.get("/emp/alltask/{id}")
def get_emp_task(id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.assigned_to == id).all()


@app.get("/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    return crud.get_tasks(db)


@app.get("/employees/names", response_model=List[EmployeeSimple])
def get_all_employees_name(db: Session = Depends(get_db)):
    return db.query(Employee.user_id, Employee.name).all()


@app.put("/task/accept/{task_id}")
def accept_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user = crud.get_user_by_username(db, current_user["username"])

    task = db.query(Task).filter(Task.id == task_id).first()
    print(task, current_user)

    task.accepted_by = current_user.id
    task.status = TaskStatus.in_progress

    db.commit()
    db.refresh(task)

    return "accepted"


@app.post("/create/task")
def create_new_task(
    request: schemas.TaskCreate,
    db: Session = Depends(get_db),
):
    employees_raw = db.query(Employee.user_id, Employee.skills).all()
    employees = []
    for emp in employees_raw:
        user_id, skill_objs = emp
        skills = [s["name"] for s in skill_objs]
        employees.append({"user_id": user_id, "skills": skills})

    title = " Organize Annual Company Retreat"
    description = "We need to plan and execute our annual company retreat, which includes venue booking, travel arrangements, budgeting, coordinating with vendors, and ensuring all teams are informed and involved. The task requires excellent communication, organization, and stakeholder management skills."
    assigned_to = granite_result(request.title, request.description, employees)

    return crud.create_task(request, db, assigned_to)
