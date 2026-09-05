import json

import config


def test_load_config_returns_defaults_when_file_missing():
    cfg = config.load_config(path="does/not/exist.json")
    assert cfg["cadence"] == "daily"
    assert cfg["weekly_day"] == "mon"
    assert cfg["weekly_limit"] == 40
    assert cfg["enabled_labs"] is None


def test_load_config_returns_defaults_when_file_is_garbage(tmp_path):
    bad = tmp_path / "config.json"
    bad.write_text("{ not valid json ", encoding="utf-8")
    cfg = config.load_config(path=str(bad))
    assert cfg == config.DEFAULTS


def test_load_config_merges_file_over_defaults(tmp_path):
    good = tmp_path / "config.json"
    good.write_text(json.dumps({"cadence": "weekly", "enabled_labs": ["xai"]}), encoding="utf-8")
    cfg = config.load_config(path=str(good))
    assert cfg["cadence"] == "weekly"          # overridden
    assert cfg["enabled_labs"] == ["xai"]      # overridden
    assert cfg["weekly_day"] == "mon"          # default preserved


def test_enabled_sites_returns_all_when_enabled_labs_is_none():
    sites = [{"name": "a"}, {"name": "b"}]
    assert config.enabled_sites(sites, {"enabled_labs": None}) == sites


def test_enabled_sites_filters_to_allowlist():
    sites = [{"name": "a"}, {"name": "b"}, {"name": "c"}]
    out = config.enabled_sites(sites, {"enabled_labs": ["a", "c"]})
    assert [s["name"] for s in out] == ["a", "c"]


def test_enabled_sites_empty_list_means_all_on():
    # An empty allowlist is treated as "no filter" (all on), never "email nothing".
    sites = [{"name": "a"}, {"name": "b"}]
    assert config.enabled_sites(sites, {"enabled_labs": []}) == sites
