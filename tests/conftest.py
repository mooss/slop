import pytest
import yaml
from pathlib import Path

@pytest.fixture(scope="session")
def partition():
    """Load the BWV-639 YAML file once for all tests."""
    path = Path(__file__).parent.parent / "data" / "music" / "bwv-639.yaml"
    with open(path) as f:
        return yaml.safe_load(f)
