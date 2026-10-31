import unittest
from math import isclose
from optimizer import distance, route_distance, nearest_neighbor, two_opt, optimize
class TestOptimizer(unittest.TestCase):
    def test_distance(self):
        self.assertEqual(distance(('A',0,0),('B',3,4)),5)
    def test_empty(self):
        self.assertEqual(optimize([('Depot',0,0)])['optimized_km'],0)
    def test_one_delivery(self):
        self.assertEqual(optimize([('Depot',0,0),('A',3,4)])['optimized_km'],10)
    def test_visits_every_stop_once(self):
        stops=[('D',0,0),('A',1,0),('B',0,2),('C',2,2)]
        result=optimize(stops)
        self.assertEqual(sorted(result['optimized_order']),[1,2,3])
    def test_no_worse_than_original(self):
        result=optimize([('D',0,0),('A',2,6),('B',7,1),('C',3,3),('E',8,7),('F',5,5)])
        self.assertLessEqual(result['optimized_km'],result['original_km']+1e-8)
    def test_two_opt_improves_crossed_route(self):
        stops=[('D',0,0),('A',0,4),('B',4,0),('C',4,4)]
        initial=[1,2,3]
        self.assertLess(route_distance(stops,two_opt(stops,initial)),route_distance(stops,initial))
    def test_invalid(self):
        with self.assertRaises(ValueError): optimize([('D',float('nan'),0)])
        with self.assertRaises(ValueError): optimize([])
    def test_duplicate_locations(self):
        result=optimize([('D',0,0),('A',0,0),('B',1,0)])
        self.assertTrue(isclose(result['optimized_km'],2))
if __name__=='__main__': unittest.main()