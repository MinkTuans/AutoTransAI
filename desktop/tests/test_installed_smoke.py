"""Portable safety checks for the installed acceptance harness."""
from pathlib import Path
import pytest
from desktop.tests.test_packaging import helper


def test_disposable_root_requires_marker_and_temp_ancestry(tmp_path):
    smoke = helper('smoke_frozen')
    root = tmp_path / 'AutoTransAI installed ü' / 'profile' / 'AutoTransAI'
    root.mkdir(parents=True)
    with pytest.raises(ValueError, match='disposable'):
        smoke.validate_data_root(root, tmp_path)
    (root.parent.parent / '.installed-smoke').write_text('AutoTransAI installed acceptance')
    assert smoke.validate_data_root(root, tmp_path) == root.resolve()
    with pytest.raises(ValueError, match='disposable'):
        smoke.validate_data_root(root, tmp_path / 'elsewhere')


def test_disposable_root_rejects_symlink_escape(tmp_path):
    smoke = helper('smoke_frozen')
    workspace = tmp_path / 'AutoTransAI installed ü'
    workspace.mkdir()
    (workspace / '.installed-smoke').write_text('AutoTransAI installed acceptance')
    outside = tmp_path / 'valuable'
    outside.mkdir()
    (workspace / 'profile').symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='disposable'):
        smoke.validate_data_root(workspace / 'profile' / 'AutoTransAI', tmp_path)
