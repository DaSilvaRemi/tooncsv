"""Tests for the CSV writer module."""

import pytest
import zipfile
from pathlib import Path
from tooncsv.writer import write_csvs


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a temporary output directory."""
    return tmp_path / "test_output"


@pytest.fixture
def sample_csvs():
    """Sample CSV data for testing."""
    return {
        "simple": "name,age\nAlice,30\nBob,25",
        "parent.child": "id,value\n1,foo\n2,bar",
        "deeply.nested.file": "col1,col2\na,b\nc,d",
    }


def test_flat_mode_basic(temp_output_dir, sample_csvs):
    """Test flat mode writes all CSVs to single directory with sanitized names."""
    out_path, zip_path = write_csvs(
        sample_csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "test.zip"),
        flat=True
    )
    
    assert out_path.exists()
    assert (out_path / "simple.csv").exists()
    assert (out_path / "parent.child.csv").exists()
    assert (out_path / "deeply.nested.file.csv").exists()


def test_nested_mode_creates_subdirectories(temp_output_dir, sample_csvs):
    """Test nested mode creates hierarchical directory structure."""
    out_path, zip_path = write_csvs(
        sample_csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "test.zip"),
        flat=False
    )
    
    assert (out_path / "simple.csv").exists()
    assert (out_path / "parent" / "child.csv").exists()
    assert (out_path / "deeply" / "nested" / "file.csv").exists()


def test_bom_encoding_utf8_sig(temp_output_dir):
    """Test BOM is included when bom=True."""
    csvs = {"test": "col1,col2\nval1,val2"}
    out_path, _ = write_csvs(
        csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "test.zip"),
        bom=True
    )
    
    with open(out_path / "test.csv", "rb") as f:
        content = f.read()
        # UTF-8 BOM is EF BB BF
        assert content.startswith(b'\xef\xbb\xbf')


def test_no_bom_encoding_utf8(temp_output_dir):
    """Test BOM is not included when bom=False."""
    csvs = {"test": "col1,col2\nval1,val2"}
    out_path, _ = write_csvs(
        csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "test.zip"),
        bom=False
    )
    
    with open(out_path / "test.csv", "rb") as f:
        content = f.read()
        # Should start with 'c' (0x63) not BOM
        assert not content.startswith(b'\xef\xbb\xbf')
        assert content.startswith(b'col1')


def test_zip_archive_created(temp_output_dir, sample_csvs):
    """Test ZIP archive is created with correct contents."""
    zip_file = temp_output_dir.parent / "archive.zip"
    out_path, zip_path = write_csvs(
        sample_csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(zip_file),
        flat=True
    )
    
    assert zip_path.exists()
    assert zip_path == zip_file
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        assert "simple.csv" in names
        assert "parent.child.csv" in names
        assert "deeply.nested.file.csv" in names


def test_zip_nested_structure(temp_output_dir, sample_csvs):
    """Test ZIP preserves nested directory structure."""
    zip_file = temp_output_dir.parent / "nested.zip"
    out_path, zip_path = write_csvs(
        sample_csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(zip_file),
        flat=False
    )
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        assert "simple.csv" in names
        assert "parent/child.csv" in names
        assert "deeply/nested/file.csv" in names


def test_file_content_preserved(temp_output_dir):
    """Test CSV content is written correctly."""
    expected_content = "name,value\ntest,123\nfoo,bar"
    csvs = {"data": expected_content}
    
    out_path, _ = write_csvs(
        csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "test.zip"),
        bom=False
    )
    
    with open(out_path / "data.csv", "r", encoding="utf-8") as f:
        actual_content = f.read()
        assert actual_content == expected_content


def test_special_characters_sanitized_flat_mode(temp_output_dir):
    """Test special characters are removed in flat mode."""
    csvs = {"file/with\\special:chars*": "data"}
    out_path, _ = write_csvs(
        csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "test.zip"),
        flat=True
    )
    
    # Should sanitize to only allowed characters
    assert (out_path / "filewithspecialchars.csv").exists()


def test_empty_csvs_dict(temp_output_dir):
    """Test handling of empty CSV dictionary."""
    out_path, zip_path = write_csvs(
        {},
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "empty.zip"),
    )
    
    assert out_path.exists()
    assert zip_path.exists()


def test_return_values_are_paths(temp_output_dir):
    """Test that return values are Path objects."""
    csvs = {"test": "data"}
    out_path, zip_path = write_csvs(
        csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "test.zip"),
    )
    
    assert isinstance(out_path, Path)
    assert isinstance(zip_path, Path)


def test_newline_handling(temp_output_dir):
    """Test that newlines are handled correctly (no extra blank lines)."""
    csv_with_newlines = "col1,col2\nrow1,val1\nrow2,val2"
    csvs = {"newlines": csv_with_newlines}
    
    out_path, _ = write_csvs(
        csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "test.zip"),
        bom=False
    )
    
    # Read in binary to check exact bytes
    with open(out_path / "newlines.csv", "rb") as f:
        content = f.read()
        # Should not have \r\r\n (double carriage return)
        assert b'\r\r\n' not in content


def test_deep_nesting_nested_mode(temp_output_dir):
    """Test deeply nested paths in nested mode."""
    csvs = {"a.b.c.d.e.f": "deep,data"}
    out_path, _ = write_csvs(
        csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "test.zip"),
        flat=False
    )
    
    expected_path = out_path / "a" / "b" / "c" / "d" / "e" / "f.csv"
    assert expected_path.exists()


def test_single_name_no_dots_nested_mode(temp_output_dir):
    """Test single name without dots in nested mode."""
    csvs = {"simple": "col1\nval1"}
    out_path, _ = write_csvs(
        csvs,
        out_dir=str(temp_output_dir),
        zip_name=str(temp_output_dir.parent / "test.zip"),
        flat=False
    )
    
    assert (out_path / "simple.csv").exists()