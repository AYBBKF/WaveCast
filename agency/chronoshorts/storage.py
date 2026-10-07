"""Dossier de production, état persistant (reprise après panne) et historique."""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from .config import Settings, get_settings

T = TypeVar("T", bound=BaseModel)


def slugify(text: str, max_len: int = 48) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:max_len] or "short"


class Production:
    """Un Short en cours : `root/` contient state.json, scenes/, audio/, final.mp4."""

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "scenes").mkdir(exist_ok=True)
        (self.root / "audio").mkdir(exist_ok=True)
        self.state_path = self.root / "state.json"
        self.state: dict[str, Any] = {}
        if self.state_path.exists():
            self.state = json.loads(self.state_path.read_text(encoding="utf-8"))

    @classmethod
    def new(cls, settings: Settings | None = None, label: str = "short") -> "Production":
        s = settings or get_settings()
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return cls(Path(s.workdir) / f"{stamp}-{slugify(label)}")

    # --- état -------------------------------------------------------------
    def save(self) -> None:
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=1), encoding="utf-8")

    def has(self, key: str) -> bool:
        return key in self.state

    def put(self, key: str, value: Any) -> None:
        if isinstance(value, BaseModel):
            value = value.model_dump(mode="json")
        self.state[key] = value
        self.save()

    def get(self, key: str, model: type[T] | None = None) -> Any:
        v = self.state.get(key)
        if v is not None and model is not None:
            return model.model_validate(v)
        return v

    def log(self, message: str) -> None:
        line = f"{datetime.now().isoformat(timespec='seconds')} {message}"
        with open(self.root / "journal.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")

    @property
    def final_video(self) -> Path:
        return self.root / "final.mp4"


class History:
    """Titres déjà produits (évite les répétitions)."""

    def __init__(self, settings: Settings | None = None):
        s = settings or get_settings()
        self.path = Path(s.workdir) / "history.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.items: list[dict[str, Any]] = []
        if self.path.exists():
            try:
                self.items = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.items = []

    def titles(self, limit: int = 40) -> list[str]:
        return [i["title"] for i in self.items[-limit:]]

    def add(self, title: str, civilization: str, production_dir: Path, delivered: bool) -> None:
        self.items.append({
            "title": title, "civilization": civilization, "dir": str(production_dir),
            "delivered": delivered, "date": datetime.now().isoformat(timespec="seconds"),
        })
        self.path.write_text(json.dumps(self.items, ensure_ascii=False, indent=1), encoding="utf-8")
