#import asyncio
import unittest
#import operator
#from cess.agent import PlanningAgent, Action, Goal, Prereq
from cess.sim import Simulation


class SimulationTests(unittest.TestCase):
   
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBuildSim(self):
        a = []
        s = Simulation(a)
        self.assertEqual(s.agents,[])
        self.assertFalse(s.isDone)

if __name__ == '__main__':
    unittest.main()

