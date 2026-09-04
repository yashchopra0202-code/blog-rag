from types import SimpleNamespace
import nuggetize


class _LLM:
    def __init__(self, text="NUGGET"):
        self.text = text
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        return SimpleNamespace(content=self.text)


def _write(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(f"---\nurl: u\nsite: s\n---\n\n{body}\n", encoding="utf-8")
    return str(p)


def test_skips_entries_that_already_have_a_nugget(tmp_path):
    f = _write(tmp_path, "a.md", "some body text")
    manifest = {"https://x/a": {"file": f, "nugget": "old"}}
    llm = _LLM()
    n = nuggetize.nuggetize_manifest(manifest, str(tmp_path), llm)
    assert n == 0
    assert llm.calls == 0
    assert manifest["https://x/a"]["nugget"] == "old"


def test_writes_nugget_for_entry_without_one(tmp_path):
    f = _write(tmp_path, "a.md", "some body text")
    manifest = {"https://x/a": {"file": f}}
    llm = _LLM("A crisp summary.")
    n = nuggetize.nuggetize_manifest(manifest, str(tmp_path), llm)
    assert n == 1
    assert manifest["https://x/a"]["nugget"] == "A crisp summary."
    assert "nugget_at" in manifest["https://x/a"]


def test_one_failure_does_not_stop_the_rest(tmp_path):
    good = _write(tmp_path, "good.md", "good body")
    manifest = {
        "https://x/bad": {"file": str(tmp_path / "missing.md")},  # parse raises
        "https://x/good": {"file": good},
    }
    llm = _LLM("ok")
    n = nuggetize.nuggetize_manifest(manifest, str(tmp_path), llm)
    assert n == 1
    assert "nugget" not in manifest["https://x/bad"]
    assert manifest["https://x/good"]["nugget"] == "ok"
