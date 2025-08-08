import os
import shutil
import tempfile
from pathlib import Path
import pytest
from giv.lib.git import GitRepository
from giv.lib.summarization import CommitSummarizer
from unittest.mock import Mock

def setup_cache_dir():
    cache_dir = Path.cwd() / ".giv" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def teardown_cache_dir():
    cache_dir = Path.cwd() / ".giv" / "cache"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)

@pytest.fixture(autouse=True)
def clean_cache():
    teardown_cache_dir()
    yield
    teardown_cache_dir()

def test_cache_cleared_for_current_and_cached():
    repo = GitRepository()
    summarizer = CommitSummarizer(repo)
    # Simulate summary and history for --current
    summarizer.git.cache_summary("--current", "summary", verbose=False)
    summarizer.git.build_commit_history("--current", verbose=False)
    cache_dir = setup_cache_dir()
    assert not (cache_dir / "--current-summary.md").exists()
    assert not (cache_dir / "--current-history.md").exists()
    # Simulate summary and history for --cached
    summarizer.git.cache_summary("--cached", "summary", verbose=False)
    summarizer.git.build_commit_history("--cached", verbose=False)
    assert not (cache_dir / "--cached-summary.md").exists()
    assert not (cache_dir / "--cached-history.md").exists()

def test_cache_preserved_if_verbose():
    repo = GitRepository()
    summarizer = CommitSummarizer(repo)
    summarizer.git.cache_summary("--current", "summary", verbose=True)
    summarizer.git.build_commit_history("--current", verbose=True)
    cache_dir = setup_cache_dir()
    assert (cache_dir / "--current-summary.md").exists()
    assert (cache_dir / "--current-history.md").exists()
    summarizer.git.cache_summary("--cached", "summary", verbose=True)
    summarizer.git.build_commit_history("--cached", verbose=True)
    assert (cache_dir / "--cached-summary.md").exists()
    assert (cache_dir / "--cached-history.md").exists()

def test_clear_cache_subcommand():
    cache_dir = setup_cache_dir()
    # Create dummy cache files
    (cache_dir / "dummy-summary.md").write_text("test")
    (cache_dir / "dummy-history.md").write_text("test")
    assert (cache_dir / "dummy-summary.md").exists()
    assert (cache_dir / "dummy-history.md").exists()
    # Run clear-cache command
    from giv.commands.clear_cache import ClearCacheCommand
    args = Mock()
    args.verbose = False
    cfg_mgr = Mock()
    cmd = ClearCacheCommand(args, cfg_mgr)
    cmd.run()
    assert not (cache_dir / "dummy-summary.md").exists()
    assert not (cache_dir / "dummy-history.md").exists()
