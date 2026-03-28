import pytest
from executor import Executor
from memory import Memory


def test_executor_simple():
    memory = Memory()
    executor = Executor(memory)
    # 使用安全表达式，禁止出现 import/open 等行为
    assert executor.run('x=1\nprint(x)') == '执行完成'
