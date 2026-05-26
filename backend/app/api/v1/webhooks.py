"""
Webhooks API — configure outbound event delivery URLs.
Copyright (C) 2024 Sarthak Doshi (github.com/SdSarthak)
SPDX-License-Identifier: AGPL-3.0-only
"""

from typing import List

from django import db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.webhook import WebhookConfig
from app.schemas.webhook import WebhookCreate, WebhookResponse

router = APIRouter()


@router.post("", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    body: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a webhook configuration for the authenticated user.

    This endpoint stores a new webhook configuration
    belonging to the current user.

    Args:
        body (WebhookCreate):
            Payload with webhook configuration data.

        current_user (User):
            Authenticated user creating the webhook.

        db (Session):
            Database session dependency.

    Returns:
        WebhookResponse:
            Created webhook configuration.

    Raises:
        HTTPException:
            Raised when the webhook configuration cannot be created.
    """
    webhook_data = body.model_dump()
    webhook_data["url"] = str(body.url)

    db_webhook = WebhookConfig(
        **webhook_data,
        user_id=current_user.id,
    )

    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)

    return db_webhook


@router.get("", response_model=List[WebhookResponse])
def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve webhook configurations for the authenticated user.

    This endpoint returns all webhook configurations
    associated with the current user.

    Args:
        current_user (User):
            Authenticated user requesting webhook data.

        db (Session):
            Database session dependency.

    Returns:
        List[WebhookResponse]:
            List of webhook configurations.
    """
    return (
        db.query(WebhookConfig)
        .filter(WebhookConfig.user_id == current_user.id)
        .all()
    )


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a webhook configuration for the authenticated user.

    This endpoint removes the specified webhook configuration
    belonging to the current user.

    Args:
        webhook_id (int):
            Unique identifier of the webhook configuration.

        current_user (User):
            Authenticated user deleting the webhook.

        db (Session):
            Database session dependency.

    Returns:
        None:
            Returns no content on successful deletion.

    Raises:
        HTTPException:
            Raised when the webhook configuration is not found.
    """
    db_webhook = (
        db.query(WebhookConfig)
        .filter(
            WebhookConfig.id == webhook_id,
            WebhookConfig.user_id == current_user.id,
        )
        .first()
    )

    if db_webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )

    db.delete(db_webhook)
    db.commit()

    return None