import unittest
from cess.agent.state import *



class TestStateUpdates(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_update_state(self):
        start= {'money':10,'time':10}
        end = update_state(start,None)
        self.assertEqual(end, start)  # no change
        
        updates = {'money':10,'time':lambda x : x['time']+2}
        expected = {'money':20,'time':12}
        end = update_state(start, updates)
        self.assertEqual(end,expected )  # no change
        
        expected2 = {'money':30,'time':14}
        end = update_state(end, updates)
        self.assertEqual(end,expected2 )  # no change
        

if __name__ == '__main__':    
    unittest.main()

