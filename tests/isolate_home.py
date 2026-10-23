"""Imported first by every test module: the whole run gets a throwaway home, so no test can
write to the real ~/.claude, ~/.gemini, ~/.config/opencode or ~/.team-workflow. Windows reads
the home from USERPROFILE, not HOME, so both are set."""
import atexit
import os
import shutil
import tempfile

if not os.environ.get("TEAM_WORKFLOW_TEST_HOME"):
    HOME = tempfile.mkdtemp(prefix="tw-test-home-")
    atexit.register(shutil.rmtree, HOME, True)
    os.environ.update(TEAM_WORKFLOW_TEST_HOME=HOME, HOME=HOME, USERPROFILE=HOME)
    os.makedirs(os.path.join(HOME, ".team-workflow"))
