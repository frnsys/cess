import unittest
from cess.agent import learn


class LearningTests(unittest.TestCase):
    def test_qlearning(self):
        # coding states and actions as integers
        states_actions = {
            1: [0,1],
            2: [0,1],
            3: [-1, -2]
        }
        rewards = {
            1: 1,
            2: 0,
            3: 10
        }

        def succ(state, action):
            return state + action

        learner = learn.QLearner(states_actions, rewards, explore=0.2)

        # all values should be initialized to 0
        for s, actions in learner.Q.items():
            for a, v in actions.items():
                self.assertEqual(v, 0)

        state = 1
        for _ in range(1000):
            action = learner.choose_action(state)
            state = succ(state, action)

        # all values should be non-zero
        for s, actions in learner.Q.items():
            for a, v in actions.items():
                self.assertNotEqual(v, 0)
