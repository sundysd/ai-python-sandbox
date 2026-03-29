import pytest
from executor import Executor
from memory import Memory


def test_executor_simple():
    memory = Memory()
    executor = Executor(memory)
    # Use a safe expression — importing, opening files, etc. should be blocked
    assert executor.run('x=1\nprint(x)') == 'Execution completed'