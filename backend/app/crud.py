import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    ItemCreate,
    Task,
    TaskCreate,
    TaskRun,
    TaskRunCreate,
    TaskRunUpdate,
    TaskUpdate,
    User,
    UserCreate,
    UserUpdate,
    Workflow,
    WorkflowCreate,
    WorkflowRun,
    WorkflowRunCreate,
    WorkflowRunUpdate,
    WorkflowStage,
    WorkflowStageCreate,
    WorkflowStageUpdate,
    WorkflowUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Workflow CRUD


def create_workflow(
    *, session: Session, workflow_in: WorkflowCreate, user_id: uuid.UUID
) -> Workflow:
    db_workflow = Workflow.model_validate(
        workflow_in, update={"created_by_id": user_id}
    )
    session.add(db_workflow)
    session.commit()
    session.refresh(db_workflow)
    return db_workflow


def update_workflow(
    *, session: Session, db_workflow: Workflow, workflow_in: WorkflowUpdate
) -> Workflow:
    workflow_data = workflow_in.model_dump(exclude_unset=True)
    db_workflow.sqlmodel_update(workflow_data)
    session.add(db_workflow)
    session.commit()
    session.refresh(db_workflow)
    return db_workflow


# WorkflowStage CRUD


def create_workflow_stage(
    *, session: Session, stage_in: WorkflowStageCreate
) -> WorkflowStage:
    db_stage = WorkflowStage.model_validate(stage_in)
    session.add(db_stage)
    session.commit()
    session.refresh(db_stage)
    return db_stage


def update_workflow_stage(
    *, session: Session, db_stage: WorkflowStage, stage_in: WorkflowStageUpdate
) -> WorkflowStage:
    stage_data = stage_in.model_dump(exclude_unset=True)
    db_stage.sqlmodel_update(stage_data)
    session.add(db_stage)
    session.commit()
    session.refresh(db_stage)
    return db_stage


# Task CRUD


def create_task(*, session: Session, task_in: TaskCreate) -> Task:
    db_task = Task.model_validate(task_in)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def update_task(*, session: Session, db_task: Task, task_in: TaskUpdate) -> Task:
    task_data = task_in.model_dump(exclude_unset=True)
    db_task.sqlmodel_update(task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


# WorkflowRun CRUD


def create_workflow_run(
    *, session: Session, run_in: WorkflowRunCreate, user_id: uuid.UUID
) -> WorkflowRun:
    db_run = WorkflowRun.model_validate(run_in, update={"started_by_id": user_id})
    session.add(db_run)
    session.commit()
    session.refresh(db_run)
    return db_run


def update_workflow_run(
    *, session: Session, db_run: WorkflowRun, run_in: WorkflowRunUpdate
) -> WorkflowRun:
    run_data = run_in.model_dump(exclude_unset=True)
    db_run.sqlmodel_update(run_data)
    session.add(db_run)
    session.commit()
    session.refresh(db_run)
    return db_run


# TaskRun CRUD


def create_task_run(*, session: Session, run_in: TaskRunCreate) -> TaskRun:
    db_run = TaskRun.model_validate(run_in)
    session.add(db_run)
    session.commit()
    session.refresh(db_run)
    return db_run


def update_task_run(
    *, session: Session, db_run: TaskRun, run_in: TaskRunUpdate
) -> TaskRun:
    run_data = run_in.model_dump(exclude_unset=True)
    db_run.sqlmodel_update(run_data)
    session.add(db_run)
    session.commit()
    session.refresh(db_run)
    return db_run
