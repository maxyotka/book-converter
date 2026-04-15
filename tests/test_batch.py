from pathlib import Path

import pytest

from book_converter.batch import build_batch


def test_build_batch_runs_all_books(tmp_path, monkeypatch):
    calls = []

    def fake_convert(input_path, output_path, cli_overrides, workdir, explicit_toml=None):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"%PDF-fake")
        calls.append(input_path.name)
        return 0

    monkeypatch.setattr("book_converter.batch.convert_single", fake_convert)

    books_dir = tmp_path / "books"
    books_dir.mkdir()
    (books_dir / "a.fb2.zip").write_bytes(b"")
    (books_dir / "b.fb2").write_bytes(b"")
    (books_dir / "ignore.txt").write_bytes(b"")

    out_dir = tmp_path / "out"
    code = build_batch(books_dir, out_dir)
    assert code == 0
    assert sorted(calls) == ["a.fb2.zip", "b.fb2"]
    assert (out_dir / "a.pdf").exists()
    assert (out_dir / "b.pdf").exists()


def test_build_batch_continues_on_error(tmp_path, monkeypatch, capsys):
    def fake_convert(input_path, output_path, cli_overrides, workdir, explicit_toml=None):
        if "bad" in input_path.name:
            raise ValueError("boom")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"ok")
        return 0

    monkeypatch.setattr("book_converter.batch.convert_single", fake_convert)

    books_dir = tmp_path / "books"
    books_dir.mkdir()
    (books_dir / "good.fb2").write_bytes(b"")
    (books_dir / "bad.fb2").write_bytes(b"")

    out_dir = tmp_path / "out"
    code = build_batch(books_dir, out_dir)
    assert code == 1
    assert (out_dir / "good.pdf").exists()
    assert not (out_dir / "bad.pdf").exists()
    err = capsys.readouterr().err
    assert "bad.fb2" in err
