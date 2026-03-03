"""Tests for Pydantic models."""

import pytest

from src.catalyst_make_client.models import (
    Organization,
    Scenario,
    Execution,
    BlueprintModule,
    Blueprint,
)


def test_organization_model():
    """Test Organization model creation."""
    org = Organization(id=1, name="Test Org")
    assert org.id == 1
    assert org.name == "Test Org"


def test_scenario_model():
    """Test Scenario model creation."""
    scenario = Scenario(id=1, name="Test Scenario", enabled=True)
    assert scenario.id == 1
    assert scenario.name == "Test Scenario"
    assert scenario.enabled is True


def test_execution_model():
    """Test Execution model creation."""
    execution = Execution(
        id=1,
        scenario_id=100,
        status="success",
        errors=[],
    )
    assert execution.id == 1
    assert execution.scenario_id == 100
    assert execution.status == "success"


def test_blueprint_module():
    """Test BlueprintModule model."""
    module = BlueprintModule(
        position=1,
        name="Twilio",
        type="trigger",
        app="twilio",
        config={"phone": "+1234567890"},
    )
    assert module.position == 1
    assert module.app == "twilio"
    assert module.config["phone"] == "+1234567890"


def test_blueprint_model():
    """Test Blueprint model."""
    blueprint = Blueprint(
        name="Lead Capture",
        description="Capture leads from forms",
        modules=[],
        connections_required=["twilio", "hubspot"],
        implementation_hours=6,
    )
    assert blueprint.name == "Lead Capture"
    assert len(blueprint.connections_required) == 2
    assert blueprint.implementation_hours == 6
