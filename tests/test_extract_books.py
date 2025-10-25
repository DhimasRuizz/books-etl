import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from include.extract_books import extract_books

@pytest.fixture
def cleanup_raw_data():
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    yield raw_dir

    for f in os.listdir(raw_dir):
        if f.startswith("books_") and f.endswith(".csv"):
            os.remove(os.path.join(raw_dir, f))

def test_extract_books_creates_csv(cleanup_raw_data):
    csv_path = extract_books()
    
    assert os.path.exists(csv_path), f"CSV file not found at {csv_path}"
    
    assert "data\\raw" in csv_path or "data/raw" in csv_path, "CSV not saved in data/raw folder"
    
    assert os.path.getsize(csv_path) > 100, "CSV file is unexpectedly small or empty"