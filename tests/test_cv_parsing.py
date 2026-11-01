import io

from career_agent.parsing.cv import extract_cv_text
from tests.conftest import make_pdf


def test_extracts_text_from_file_like_object():
    text = extract_cv_text(io.BytesIO(make_pdf("Jane Doe Python Engineer")))

    assert "Jane Doe Python Engineer" in text


def test_extracts_text_from_path(tmp_path):
    path = tmp_path / "cv.pdf"
    path.write_bytes(make_pdf("Hello CV"))

    assert "Hello CV" in extract_cv_text(str(path))
