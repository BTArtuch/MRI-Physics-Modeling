import json
from pathlib import Path
from typing import TypeVar, Type

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


def save_model_json(model: BaseModel, path: Path) -> None:
    """
    Save a Pydantic model to a JSON file.
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    json_text = model.model_dump_json(indent=4)

    path.write_text(json_text, encoding="utf-8")


def load_model_json(model_class: Type[T], path: Path) -> T:
    """
    Load a Pydantic model from a JSON file.
    """

    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    json_text = path.read_text(encoding="utf-8")

    return model_class.model_validate_json(json_text)


def save_dict_json(data: dict, path: Path) -> None:
    """
    Save a plain dictionary to a JSON file.
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_dict_json(path: Path) -> dict:
    """
    Load a plain dictionary from a JSON file.
    """

    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)