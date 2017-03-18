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
        a = Action(name=None,prereqs=None,outcomes=None,cost=None)
        #no-prereqs, any value OK
        self.assertTrue(a.satisfied(None))
        self.assertTrue( a.satisfied({'dog':True}) ) 
        self.assertEqual(a.cost(),0, 'None is a 0 cost')
        self.assertEqual(str(a), 'Action(untitled action)')
        
    def testActionSimple(self):
        timePre = Prereq(int.__ge__, 30)
        
        a = Action('work', {'time': timePre}, ([{'cash': 100}], [1.]))
        self.assertTrue( a.satisfied({'time':50}) ) 
        self.assertFalse( a.satisfied({'dog':True}) ) #no satisfying time entry
        self.assertFalse( a.satisfied(None) ) #robsut check 
        self.assertEqual(a.cost(), 1) 
        self.assertEqual(str(a), 'Action(work)')

    def testActionBrokenStuff(self):
        timePre = Prereq(int.__ge__, 30)
        a = Action('work', {'time': timePre}, ([{'cash': 100}], [1.]))
        
        #I don't like how this throws, noncompatible compares fail
        with self.assertRaises(Exception) as context:
            sat = a.satisfied( {'time':None}  ) #robust check

            self.assertTrue("'descriptor '__ge__' requires a 'int' object but received a 'NoneType'" in context.exception)

if __name__ == '__main__':
    unittest.main()
