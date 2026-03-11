import os, sys, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@pytest.fixture(autouse=True)
def iso(tmp_path, monkeypatch):
    import utils.learning as L
    d = str(tmp_path / "ld"); os.makedirs(d)
    monkeypatch.setattr(L, "LEARNING_DIR", d)
    monkeypatch.setattr(L, "OVERRIDE_FILE", os.path.join(d,"overrides.csv"))
    monkeypatch.setattr(L, "MODEL_FILE", os.path.join(d,"model.json"))

from utils.learning import record_override, load_overrides, suggest_action, load_model, get_stats

def test_record_creates():
    record_override("file_organizer","A","B","x.pdf")
    assert len(load_overrides()) == 1

def test_multiple():
    record_override("m","A","B","x.pdf"); record_override("m","A","B","y.pdf")
    assert len(load_overrides()) == 2

def test_no_data_default():
    assert suggest_action("m","x.pdf","default") == "default"

def test_learns():
    for _ in range(3): record_override("file_organizer","A","B","x.pdf")
    assert suggest_action("file_organizer","x.pdf","A") == "B"

def test_empty_model():  assert load_model() == {}

def test_model_after():
    record_override("m","A","B","x.pdf"); m = load_model()
    assert "m::.pdf" in m and m["m::.pdf"]["B"] == 1

def test_stats_empty():  assert get_stats()["total_overrides"] == 0

def test_stats():
    record_override("m1","A","B","x.pdf"); record_override("m2","C","D","y")
    s = get_stats(); assert s["total_overrides"]==2 and "m1" in s["by_module"]
