import unittest
from cess.agent import Agent
from tests import async, TestAgent


class AgentTests(unittest.TestCase):

    @async
    def test_get_single(self):
        agent = Agent(state={'aa': 1, 'bb': 2, 'cc': 3})
        result = yield from agent.get('aa')
        self.assertEqual(result, 1)

    @async
    def test_get_multiple(self):
        agent = Agent(state={'aa': 1, 'bb': 2, 'cc': 3})
        aa, bb = yield from agent.get('aa', 'bb')
        self.assertEqual(aa, 1)
        self.assertEqual(bb, 2)

    @async
    def test_set(self):
        agent = Agent(state={'aa': 1, 'bb': 2, 'cc': 3})
        yield from agent.set(aa=10, bb=20)
        aa, bb = yield from agent.get('aa', 'bb')
        self.assertEqual(aa, 10)
        self.assertEqual(bb, 20)

    @async
    def test_call(self):
        agent = TestAgent()
        result = yield from agent.call('multiply', 10)
        self.assertEqual(result, 20)

if __name__ == '__main__':
    unittest.main()
