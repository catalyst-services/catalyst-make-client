"""Pydantic models for Make.com API responses."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Organization(BaseModel):
    """Make.com Organization model."""

    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    slug: str | None = None


class Scenario(BaseModel):
    """Make.com Scenario (workflow) model."""

    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    description: str | None = None
    enabled: bool = True


class Execution(BaseModel):
    """Make.com Scenario Execution model."""

    model_config = ConfigDict(extra="allow")

    id: int
    scenario_id: int
    status: str  # success, error, partial_error, etc
    start_time: str | None = None
    end_time: str | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)


class BlueprintModule(BaseModel):
    """Blueprint module (step in workflow)."""

    position: int
    name: str
    type: str
    app: str
    config: dict[str, Any]


class Blueprint(BaseModel):
    """Workflow blueprint for deployment."""

    model_config = ConfigDict(extra="allow")

    name: str
    description: str
    modules: list[BlueprintModule]
    connections_required: list[str]
    implementation_hours: int
