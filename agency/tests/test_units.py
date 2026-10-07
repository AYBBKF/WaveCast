from pathlib import Path

import pytest

from chronoshorts import schemas as S
from chronoshorts.config import Settings
from chronoshorts.llm import LLM, CostTracker, UsageRecord
from chronoshorts.media.subtitles import build_ass, build_srt, group_cues
from chronoshorts.pipeline import _align_by_scene, _repair_storyboard, _repair_voice_script
from chronoshorts.providers.tts import WordTiming, _words_from_char_alignment, estimate_word_timings
from chronoshorts.providers.video import ReplicateVideo, MotionSpec
from chronoshorts.scheduler import next_run
from chronoshorts.storage import slugify


def test_slugify():
    assert slugify("À quoi ressemblait Cordoue ?") == "a-quoi-ressemblait-cordoue"


def test_word_timings_from_char_alignment():
    al = {"characters": list("ab cd"), "character_start_times_seconds": [0, .1, .2, .3, .4],
          "character_end_times_seconds": [.1, .2, .3, .4, .5]}
    w = _words_from_char_alignment(al)
    assert [x.word for x in w] == ["ab", "cd"]
    assert w[1].start == .3 and w[1].end == .5


def test_estimate_word_timings_sum():
    w = estimate_word_timings("un deux trois", 3.0)
    assert len(w) == 3 and abs(w[-1].end - 3.0) < 1e-6


def test_group_cues_breaks_on_punctuation():
    words = [WordTiming(t, i, i + 1) for i, t in enumerate("Bonjour. Voici une phrase assez longue".split())]
    cues = group_cues(words, max_words=4)
    assert [len(c.words) for c in cues] == [1, 4, 1]


def test_ass_and_srt(tmp_path: Path):
    words = [WordTiming(t, i * .5, i * .5 + .4) for i, t in enumerate("Imaginez Cordoue en l'an mille".split())]
    ass = build_ass(words, tmp_path / "s.ass", width=1080, height=1920, font="DejaVu Sans", rtl=True)
    txt = ass.read_text()
    assert "Dialogue:" in txt and "‫" in txt and "PlayResY: 1920" in txt
    srt = build_srt(words, tmp_path / "s.srt").read_text()
    assert "00:00:00,000 --> " in srt


def test_repair_storyboard_splits_long_scene():
    s = Settings(_env_file=None, verify_models=False)
    long = " ".join(["mot"] * 30)
    board = S.Storyboard(scenes=[S.Scene(index=7, narration=long, target_seconds=4, narrative_goal="g",
                                         characters=[], setting="x", visible_action="a", emotion="joie",
                                         camera="zoom lent", transition_out="cut")] * 8, rhythm_notes="")
    script = S.Script(title="t", beats=[S.ScriptBeat(role="hook", narration=long)] * 5, full_narration=long, word_count=30)
    out = _repair_storyboard(board, script, 0.42, s)
    assert len(out.scenes) == 16 and [sc.index for sc in out.scenes] == list(range(16))
    assert all(sc.target_seconds <= 8 for sc in out.scenes)
    assert out.scenes[-1].transition_out == "fondu noir"


def test_align_and_voice_repair():
    board = S.Storyboard(scenes=[S.Scene(index=i, narration=f"n{i}", target_seconds=4, narrative_goal="g",
                                         characters=[], setting="x", visible_action="a", emotion="joie",
                                         camera="zoom lent", transition_out="cut") for i in range(8)], rhythm_notes="")
    pack = S.PromptPack(scenes=[S.ScenePrompts(scene_index=0, image_prompt="p", video_prompt="v",
                                               negative_prompt="n", camera_motion="c")])
    aligned = _align_by_scene(pack, board, "scenes", "scene_index")
    assert [p.scene_index for p in aligned.scenes] == list(range(8))
    voice = _repair_voice_script(S.VoiceScript(narrator_persona="p", segments=[]), board)
    assert [v.text for v in voice.segments] == [f"n{i}" for i in range(8)]


def test_cost_tracker():
    c = CostTracker()
    c.add(UsageRecord("a", "claude-haiku-5-5", 1_000_000, 0, 0, 0, 1))
    c.add(UsageRecord("b", "claude-opus-5-5", 0, 1_000_000, 0, 0, 1))
    assert abs(c.total_usd() - 20.10) < 1e-6
    assert c.report()["per_agent"]["a"]["calls"] == 1


def test_request_options_per_model():
    s = Settings(_env_file=None, verify_models=False, anthropic_api_key="x")
    llm = LLM(s)
    o = llm._request_options("claude-opus-5-5", "director", web_search=True)
    assert o["thinking"] == {"type": "adaptive"} and o["output_config"] == {"effort": "high"}
    assert o["tools"][0]["type"] == "web_search_20260209"
    assert o["extra_body"] == {"fallbacks": "default"}
    o = llm._request_options("claude-haiku-5-5", "worker", web_search=True)
    assert o["tools"][0]["type"] == "web_search_20250305" and "extra_body" not in o
    o = llm._request_options("claude-haiku-4-5", "worker", web_search=False)
    assert "thinking" not in o and "output_config" not in o


def test_replicate_video_inputs():
    s = Settings(_env_file=None, verify_models=False)
    p = ReplicateVideo(s)
    spec = MotionSpec(prompt="p", negative="n", seconds=5.6)
    assert p._inputs("bytedance/seedance-1-pro", "http://img", spec)["duration"] == 6
    assert p._inputs("kwaivgi/kling-v2.1", "http://img", spec)["duration"] == 10
    assert p._inputs("minimax/hailuo-02", "http://img", spec)["first_frame_image"] == "http://img"


def test_next_run():
    from datetime import datetime
    t = next_run(datetime(2026, 1, 1, 10, 0), [9, 18])
    assert t.hour == 18 and t.day == 1
    t = next_run(datetime(2026, 1, 1, 19, 0), [9, 18])
    assert t.hour == 9 and t.day == 2


@pytest.mark.parametrize("lang,rtl", [("fr", False), ("ar", True)])
def test_settings_language(lang, rtl):
    s = Settings(_env_file=None, language=lang)
    assert s.is_rtl is rtl and s.language_name
