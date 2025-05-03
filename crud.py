import json
from sqlalchemy.orm import Session
from models import User, Task, Employee, TaskStatus
from schemas import TaskCreate, UserCreate, EmployeeCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_employee_by_id(id: int, db: Session):
    return db.query(Employee).filter(Employee.user_id == id).first()


def get_employees(db: Session):
    return db.query(Employee).all()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_tasks(db: Session):
    return db.query(Task).all()


def create_task(task: TaskCreate, db: Session, assigned_to: int):
    print(task)
    assigned_to = int(task.assigned_to) if task.mandatory else assigned_to
    status = TaskStatus.in_progress if task.mandatory else TaskStatus.unassigned
    accepted_by = task.assigned_to if task.mandatory else None

    db_task = Task(
        title=task.title,
        description=task.description,
        mandatory=task.mandatory,
        deadline=task.deadline,
        assigned_to=assigned_to,
        status=status,
        accepted_by=accepted_by,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def create_user(user: UserCreate, db: Session):
    db_user = User(
        username=user.username, password_hash=user.password_hash, role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_task(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()


def create_employee(employee: EmployeeCreate, db: Session):
    employee_dict = employee.dict()

    # Then prepare for database insertion
    db_employee = {
        "user_id": employee_dict["user_id"],
        "bio": employee_dict["bio"],
        "skills": json.dumps([skill for skill in employee_dict["skills"]]),
        "email": employee_dict["contactInfo"]["email"],
        "phone": employee_dict["contactInfo"]["phone"],
    }
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_task_by_id(id: int, db: Session):
    ongoing = (
        db.query(Task)
        .filter(Task.accepted_by == id, Task.status == TaskStatus.in_progress)
        .all()
    )
    assigned = (
        db.query(Task).filter(Task.assigned_to == id, Task.accepted_by == None).all()
    )
    completed = (
        db.query(Task)
        .filter(
            Task.accepted_by == id,
            Task.status.in_(
                [
                    TaskStatus.completed_after_deadline,
                    TaskStatus.completed_before_deadline,
                ]
            ),
        )
        .all()
    )

    return {"ongoing": ongoing, "assigned": assigned, "completed": completed}
