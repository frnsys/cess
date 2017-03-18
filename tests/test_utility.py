import unittest
import operator
from cess import Goal, Prereq
from cess.agent import utility
from cess.agent.outcome import outcome_dist

ufuncs = {
    'cash': lambda x: x
}


class UtilityTests(unittest.TestCase):
    def test_change_utility(self):
        state = {'cash': 0}
        to_state = {'cash': 1000}
        util = utility.change_utility(ufuncs, state, to_state)
        self.assertEqual(util, 1000)

    def test_expected_utility(self):
        state = {'cash': 0}
        outcomes = outcome_dist(state, [{'cash': 1000}, {'cash': 2000}], [0.5, 0.5])
        exp_util = utility.expected_utility(ufuncs, state, outcomes)
        self.assertEqual(exp_util, 1500)

    def test_state_utility_for_goal(self):
        goal = Goal(
            'test_goal',
            prereqs={'sup': Prereq(operator.lt, 10)},
            outcomes=([{'cash': 1000}], [1.]),
            failures=None,
            time=None)

        # closer to the goal
        state = {'sup': 11, 'cash':0}
        util1 = utility.goal_utility(ufuncs, state, goal)

        # further from the goal
        state = {'sup': 20, 'cash':0}
        util2 = utility.goal_utility(ufuncs, state, goal)

        self.assertTrue(util1 > util2)

if __name__ == '__main__':
    unittest.main()
