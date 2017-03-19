import math


class Prereq():
    """a prerequisite, condiiton for a goal or an action.
    Class to represent a prerequisiste, and check if it was 
    satisified."""

    def __init__(self, comparator, target):
        """
        @param comparator is a 2-arity predicate;
        @target is the value to compare to.
        generally you would use something like `operator.le`
        as a comparator."""
        self.target = target
        self.comparator = comparator

    def __call__(self, val):
        '''True if the passed value causes this to Prereq be satisifed'''
        if val is  None:
            return False
        return self.comparator(val, self.target)


    def __and__(self, other_prereq):
        """returns a new prereq AND'd with this prereq"""
        return AndPrereq(self, other_prereq)

    def __or__(self, other_prereq):
        """returns a new prereq OR'd with this prereq"""
        return OrPrereq(self, other_prereq)

    def distance(self, val):
        """returns squared normalized distance to value;
        it can be used to calculate euclidean distance"""
        # if satisfied, distance = 0
        if self(val):
            return 0
        if self.target == 0:
            return (self.target - val)**2
        return ((self.target - val)/self.target)**2


class OrPrereq(Prereq):
    """a multi-prerequisite with an OR relationship"""
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __call__(self, val):
        return self.p1(val) or self.p2(val)

    def distance(self, val):
        """for OR relationship, minimum of distances is the distance"""
        return min(self.p1.distance(val), self.p2.distance(val))


class AndPrereq(Prereq):
    """a multi-prerequisite with an AND relationship"""
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __call__(self, val):
        return self.p1(val) and self.p2(val)

    def distance(self, val):
        """for AND relationship, the sum of the distances is the distance"""
        return self.p1.distance(val) + self.p2.distance(val)


def distance_to_prereqs(state, prereqs):
    """(euclidean) distance of a state to a set of prerequisites"""
    dist_sum = 0
    for k in prereqs.keys():
        pre, val = prereqs[k], state[k]
        dist_sum += pre.distance(val)
    return math.sqrt(dist_sum)
