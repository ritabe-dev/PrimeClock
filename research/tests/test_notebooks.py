import json
from pathlib import Path


def test_notebooks_are_valid_json():
    notebooks = sorted((Path(__file__).parents[1] / "notebooks").glob("*.ipynb"))
    assert notebooks
    for notebook in notebooks:
        payload = json.loads(notebook.read_text(encoding="utf-8"))
        assert payload["nbformat"] == 4
        assert payload["cells"]

