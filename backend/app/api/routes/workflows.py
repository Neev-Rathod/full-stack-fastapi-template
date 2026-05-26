import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Workflow,
    WorkflowCreate,
    WorkflowPublic,
    WorkflowsPublic,
    WorkflowUpdate,
)

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/", response_model=WorkflowsPublic)
def read_workflows(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve workflows.
    """
    count_statement = (
        select(func.count())
        .select_from(Workflow)
        .where(Workflow.created_by_id == current_user.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Workflow)
        .where(Workflow.created_by_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    workflows = session.exec(statement).all()
    return WorkflowsPublic(data=workflows, count=count)


@router.post("/", response_model=WorkflowPublic)
def create_workflow(
    *, session: SessionDep, current_user: CurrentUser, workflow_in: WorkflowCreate
) -> Any:
    """
    Create new workflow.
    """
    workflow = crud.create_workflow(
        session=session, workflow_in=workflow_in, user_id=current_user.id
    )
    return workflow


@router.get("/{id}", response_model=WorkflowPublic)
def read_workflow(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get workflow by ID.
    """
    workflow = session.get(Workflow, id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.created_by_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return workflow


@router.put("/{id}", response_model=WorkflowPublic)
def update_workflow(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    workflow_in: WorkflowUpdate,
) -> Any:
    """
    Update a workflow.
    """
    workflow = session.get(Workflow, id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.created_by_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    workflow = crud.update_workflow(
        session=session, db_workflow=workflow, workflow_in=workflow_in
    )
    return workflow


@router.delete("/{id}")
def delete_workflow(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Delete a workflow.
    """
    workflow = session.get(Workflow, id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.created_by_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(workflow)
    session.commit()
    return {"message": "Workflow deleted successfully"}
