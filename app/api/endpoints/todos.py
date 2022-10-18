from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies

router = APIRouter(prefix="/todos", tags=["todos"])


def get_todo_from_id(
    todo_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Common dependency to check that the ToDo item exists and
    that the current user has access to it.
    """
    todo = models.ToDo.get_by_id(db, id=todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ToDo not found",
        )
    if todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ToDo does not belong to current user",
        )

    return todo


@router.post(
    "",
    response_model=schemas.ToDoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ToDo",
    response_description="The new created ToDo",
)
def create_todo(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    todo_in: schemas.ToDoCreate,
):
    todo = models.ToDo.create(db, todo_in, current_user.id)
    return todo


@router.get(
    "",
    response_model=list[schemas.ToDoOut],
    summary="Get a range of todos for the current user",
    response_description="List of todos",
)
def read_todos(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=0),
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
):
    return models.ToDo.get_multiple(
        db,
        user_id=current_user.id,
        offset=offset,
        limit=limit,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )


@router.get(
    "/{todo_id}",
    response_model=schemas.ToDoOut,
    summary="Get a specific ToDo by ID",
    response_description="The ToDo with the specified ID",
)
def read_todo_by_id(
    todo: models.ToDo = Depends(get_todo_from_id),
):

    return todo


@router.put(
    "/{todo_id}",
    response_model=schemas.ToDoOut,
    summary="Update a specific ToDo by ID",
    response_description="The updated ToDo with the specified ID",
)
def update_todo_by_id(
    update_data: schemas.ToDoUpdate,
    todo: models.ToDo = Depends(get_todo_from_id),
    db: Session = Depends(dependencies.get_db),
):
    todo = models.ToDo.update(db, current=todo, new=update_data)
    return todo


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific ToDo by ID",
)
def delete_todo_by_id(
    todo: models.ToDo = Depends(get_todo_from_id),
    db: Session = Depends(dependencies.get_db),
):
    models.ToDo.delete(db, todo)
    # the body will be empty when using status code 204
