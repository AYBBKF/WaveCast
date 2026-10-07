import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chronoshorts.config import Settings, set_settings  # noqa: E402


@pytest.fixture
def offline_settings(tmp_path: Path) -> Settings:
    s = Settings(
        tts_provider="silent", image_provider="placeholder", video_provider="kenburns",
        workdir=tmp_path / "productions", assets_dir=tmp_path / "assets",
        verify_models=False, max_concurrency=3, fps=24, width=540, height=960,
        _env_file=None,
    )
    set_settings(s)
    return s
