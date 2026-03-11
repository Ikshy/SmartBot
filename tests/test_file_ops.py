import os, sys, shutil, tempfile, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.file_ops import (move_file, copy_file, delete_file, rename_file,
                             organize_folder, list_files, _get_category, _resolve_conflict)

@pytest.fixture
def dirs():
    s, d = tempfile.mkdtemp(), tempfile.mkdtemp()
    yield s, d
    shutil.rmtree(s, ignore_errors=True); shutil.rmtree(d, ignore_errors=True)

def mkf(d, name, c="x"):
    p = os.path.join(d, name)
    open(p,"w").write(c); return p

def test_category_image():       assert _get_category("a.jpg") == "images"
def test_category_doc():         assert _get_category("a.pdf") == "documents"
def test_category_unknown():     assert _get_category("a.xyz123") == "misc"
def test_no_conflict(dirs):      p = os.path.join(dirs[0],"x.txt"); assert _resolve_conflict(p)==p
def test_conflict(dirs):         p = mkf(dirs[0],"x.txt"); assert _resolve_conflict(p) != p

def test_move(dirs):
    f = mkf(dirs[0],"t.txt"); r = move_file(f, dirs[1])
    assert r and os.path.isfile(r) and not os.path.isfile(f)

def test_move_conflict(dirs):
    mkf(dirs[1],"d.txt"); f = mkf(dirs[0],"d.txt"); r = move_file(f, dirs[1])
    assert r and r != os.path.join(dirs[1],"d.txt")

def test_move_missing(dirs):     assert move_file("/no/file.txt", dirs[1]) is None

def test_copy(dirs):
    f = mkf(dirs[0],"c.txt"); r = copy_file(f, dirs[1])
    assert r and os.path.isfile(r) and os.path.isfile(f)

def test_delete(dirs):
    f = mkf(dirs[0],"b.txt"); assert delete_file(f) and not os.path.isfile(f)

def test_delete_missing():       assert not delete_file("/no/file.txt")

def test_rename(dirs):
    f = mkf(dirs[0],"old.txt"); r = rename_file(f,"new.txt")
    assert r and "new.txt" in r

def test_organize(dirs):
    for n in ["a.jpg","b.pdf","c.mp3"]: mkf(dirs[0], n)
    s = organize_folder(dirs[0], dirs[1])
    assert "images" in s and "documents" in s and "audio" in s

def test_organize_empty(dirs):   assert organize_folder(dirs[0], dirs[1]) == {}
def test_list(dirs):
    mkf(dirs[0],"a.txt"); mkf(dirs[0],"b.txt")
    assert len(list_files(dirs[0])) == 2