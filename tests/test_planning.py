import asyncio
import unittest
import operator
from cess.agent import PlanningAgent, Action, Goal, Prereq


class ActionTests(unittest.TestCase):
    """ tests Aciton object"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testActionEmpty(self):
        a = Action(None,None,None)
        #no-prereqs, any value OK
        self.assertTrue(a.satisfied(None))
        self.assertTrue( a.satisfied({'dog':True}) ) 
        
    def testActionSimple(self):
        timePre = Prereq(int.__ge__, 30)
        
        a = Action('work', {'time': timePre}, ([{'cash': 100}], [1.]))
        self.assertTrue( a.satisfied({'time':50}) ) 
        self.assertFalse( a.satisfied({'dog':True}) ) #no satisfying time entry. Fail 
        


class PlanningAgentTests(unittest.TestCase):

    def _coro(self, coro):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

    def test_score_successor(self):

        utility_funcs = {
            'cash': lambda x: x
        }
        action = Action('work', {}, ([{'cash': 100}], [1.]))
        goal = Goal('money', {'cash': Prereq(operator.ge, 200)}, ([{'cash': 1000}], [1.]))
        agent = PlanningAgent({'cash':0}, [action], [goal], utility_funcs)

        from_state = {'cash': 0}
        state_a = {'cash': -100}
        state_b = {'cash': 100}
        state_c = {'cash': 200}
        state_d = {'cash': 300}

        self.assertTrue(agent._score_successor(from_state, state_a) < agent._score_successor(from_state, state_b))
        self.assertTrue(agent._score_successor(from_state, state_b) < agent._score_successor(from_state, state_c))
        self.assertTrue(agent._score_successor(from_state, state_c) < agent._score_successor(from_state, state_d))

    def test_plan(self):
        utility_funcs = {
            'cash': lambda x: x
        }
        action = Action('work', {}, ([{'cash': 100}, {'cash': 50}], [0.5, 0.5]))

        # an action not achievable immediately, should become a goal
        action_goal = Action('hire help', {'cash': Prereq(operator.ge, 200)}, ([{'cash': 1000}], [1.]))
        goal = Goal('money', {'cash': Prereq(operator.ge, 200)}, ([{'cash': 1000}], [1.]))

        agent = PlanningAgent({'cash':0}, [action, action_goal], [goal], utility_funcs)
        plan, goals = agent.plan(agent._state, agent.goals, depth=3)
        expected_plan = [(action, ({'cash': 75.0}, {goal})), (action, ({'cash': 150.0}, {goal})), (action, ({'cash': 225.0}, {goal}))]

        # goals should contain the desired, but not yet satisfiable, action
        self.assertEqual(goals, set([goal, action_goal]))

        # returned plan should not contain unsatisfiable actions
        self.assertEqual(plan, expected_plan)

if __name__ == '__main__':
    unittest.main()
