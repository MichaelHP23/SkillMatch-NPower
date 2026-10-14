from streamlit.testing.v1 import AppTest

from src.db import DEFAULT_DB_PATH


def _db_state():
    return DEFAULT_DB_PATH.stat().st_mtime_ns if DEFAULT_DB_PATH.exists() else None


def test_app_runs_on_sample_data_and_leaves_no_database_behind():
    before = _db_state()
    at = AppTest.from_file("../app.py", default_timeout=60).run()
    at.sidebar.button[0].click().run()

    assert not at.exception
    assert not at.error
    assert at.session_state.ranked_df is not None
    # The app must not write student records into db/ (NFR-7): its
    # database lives in a temporary folder that is deleted after the run.
    assert _db_state() == before
