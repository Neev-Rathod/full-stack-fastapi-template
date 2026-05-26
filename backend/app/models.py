import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    workflows: list["Workflow"] = Relationship(
        back_populates="created_by", cascade_delete=True
    )
    tasks: list["Task"] = Relationship(back_populates="assigned_to")
    workflow_runs: list["WorkflowRun"] = Relationship(
        back_populates="started_by", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Workflow Models


class WorkflowBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    category: str | None = Field(default=None, max_length=255)
    is_template: bool = False
    visibility: str = Field(default="private", max_length=50)


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(WorkflowBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class Workflow(WorkflowBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    created_by: User | None = Relationship(back_populates="workflows")
    stages: list["WorkflowStage"] = Relationship(
        back_populates="workflow", cascade_delete=True
    )
    runs: list["WorkflowRun"] = Relationship(
        back_populates="workflow", cascade_delete=True
    )


class WorkflowPublic(WorkflowBase):
    id: uuid.UUID
    created_by_id: uuid.UUID
    created_at: datetime


class WorkflowsPublic(SQLModel):
    data: list[WorkflowPublic]
    count: int


class WorkflowStageBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    position: int
    color: str | None = Field(default=None, max_length=50)
    completion_rule: str | None = Field(default=None, max_length=255)


class WorkflowStageCreate(WorkflowStageBase):
    workflow_id: uuid.UUID


class WorkflowStageUpdate(WorkflowStageBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    position: int | None = None  # type: ignore


class WorkflowStage(WorkflowStageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workflow_id: uuid.UUID = Field(
        foreign_key="workflow.id", nullable=False, ondelete="CASCADE"
    )

    workflow: Workflow | None = Relationship(back_populates="stages")
    tasks: list["Task"] = Relationship(back_populates="stage", cascade_delete=True)


class WorkflowStagePublic(WorkflowStageBase):
    id: uuid.UUID
    workflow_id: uuid.UUID


class WorkflowStagesPublic(SQLModel):
    data: list[WorkflowStagePublic]
    count: int


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    priority: str | None = Field(default=None, max_length=50)
    status: str | None = Field(default=None, max_length=50)
    due_date: datetime | None = None
    assigned_to_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )


class TaskCreate(TaskBase):
    stage_id: uuid.UUID


class TaskUpdate(TaskBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    stage_id: uuid.UUID = Field(
        foreign_key="workflowstage.id", nullable=False, ondelete="CASCADE"
    )

    stage: WorkflowStage | None = Relationship(back_populates="tasks")
    assigned_to: User | None = Relationship(back_populates="tasks")
    task_runs: list["TaskRun"] = Relationship(
        back_populates="task", cascade_delete=True
    )


class TaskPublic(TaskBase):
    id: uuid.UUID
    stage_id: uuid.UUID


class TasksPublic(SQLModel):
    data: list[TaskPublic]
    count: int


class WorkflowRunBase(SQLModel):
    status: str = Field(min_length=1, max_length=50)


class WorkflowRunCreate(WorkflowRunBase):
    workflow_id: uuid.UUID


class WorkflowRunUpdate(WorkflowRunBase):
    status: str | None = Field(default=None, min_length=1, max_length=50)  # type: ignore


class WorkflowRun(WorkflowRunBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workflow_id: uuid.UUID = Field(
        foreign_key="workflow.id", nullable=False, ondelete="CASCADE"
    )
    started_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    workflow: Workflow | None = Relationship(back_populates="runs")
    started_by: User | None = Relationship(back_populates="workflow_runs")
    task_runs: list["TaskRun"] = Relationship(
        back_populates="workflow_run", cascade_delete=True
    )


class WorkflowRunPublic(WorkflowRunBase):
    id: uuid.UUID
    workflow_id: uuid.UUID
    started_by_id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None


class WorkflowRunsPublic(SQLModel):
    data: list[WorkflowRunPublic]
    count: int


class TaskRunBase(SQLModel):
    status: str = Field(min_length=1, max_length=50)
    notes: str | None = Field(default=None, max_length=1000)


class TaskRunCreate(TaskRunBase):
    workflow_run_id: uuid.UUID
    task_id: uuid.UUID


class TaskRunUpdate(TaskRunBase):
    status: str | None = Field(default=None, min_length=1, max_length=50)  # type: ignore


class TaskRun(TaskRunBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workflow_run_id: uuid.UUID = Field(
        foreign_key="workflowrun.id", nullable=False, ondelete="CASCADE"
    )
    task_id: uuid.UUID = Field(
        foreign_key="task.id", nullable=False, ondelete="CASCADE"
    )
    completed_at: datetime | None = None

    workflow_run: WorkflowRun | None = Relationship(back_populates="task_runs")
    task: Task | None = Relationship(back_populates="task_runs")


class TaskRunPublic(TaskRunBase):
    id: uuid.UUID
    workflow_run_id: uuid.UUID
    task_id: uuid.UUID
    completed_at: datetime | None


class TaskRunsPublic(SQLModel):
    data: list[TaskRunPublic]
    count: int
