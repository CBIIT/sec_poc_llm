import dataclasses
from dataclasses import dataclass
from typing import Any, Union
import json


def is_model(line: str):
    is_source = line.startswith("SourceText(") and line.endswith(")")
    is_answer = line.startswith("Answer(") and line.endswith(")")
    return is_source or is_answer


class ModelJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            modeljson = dataclasses.asdict(o)
            mark4del = []
            for key, value in modeljson.items():
                if not value or value.lower() == "none":
                    mark4del.append(key)
            for key in mark4del:
                del modeljson[key]
            return modeljson
        return super().default(o)


def represent(o: Union["SourceText", "Answer"]) -> str:
    fields = dataclasses.fields(o)
    values = dataclasses.astuple(o)
    fields_vals = list(zip(fields, values))
    if isinstance(o, SourceText):
        base = "SourceText("
    else:
        base = "Answer("
    for idx, (key, value) in enumerate(fields_vals):
        if not value or value == "None":
            continue
        else:
            base += f", {key.name}={value}" if idx > 0 else f"{key.name}={value}"
    return base + ")"


@dataclass
class SourceText:
    value: str = ""

    def __repr__(self) -> str:
        return represent(self)


@dataclass
class Answer:
    value: str = ""
    Cohort: Any = None
    Min: Any = None
    Max: Any = None
    MinSize: Any = None
    MaxSize: Any = None
    MinCount: Any = None
    MaxCount: Any = None

    def __repr__(self) -> str:
        return represent(self)
