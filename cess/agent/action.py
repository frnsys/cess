from .outcome import resolve_outcomes, expected_state, outcome_dist


class PrereqsUnsatisfied(Exception):
    pass


class Action():
    """
    An action an agent can take. actions has a distribution
    of possible outcomes and may have prerequisites.
    """

    def __init__(self, name, prereqs, outcomes, cost=1):
        """`
        @param 'name' name to reference this action by
        @param prerequs  dict of 'value-name':cess.Prereq(compare_lamda, value) object
        @param outcomes a tuple of `(updates, dist)`,
        where `updates`  = list of update dictionaries where key in ? and value is ??
        where `dist` is either 
         - a list of probabilities for each corresponding state update,
         - a callable which returns such a list of probabilities.
        """
        if name is None:
            name = 'untitled action'
        if prereqs is None:
            prereqs = {}
        if outcomes is None or len(outcomes) < 2:
            outcomes = (None,None) #set defaults
        if cost is None:
            cost = 0
        self.name = name
        self.prereqs = prereqs
        self.updates, self.dist = outcomes
        self._cost = cost

    def __repr__(self):
        return 'Action({})'.format(self.name)

    def __call__(self, state):
        """complete this action (if its prereqs are satisfied),
        @returns an outcome state"""
        if not self.satisfied(state):
            raise PrereqsUnsatisfied
        return resolve_outcomes(state, self.updates, self.dist)
 
    def satisfied(self, state):
        """ True if this Action's prerequisistes are satisifed by 
        the passed state.
        @parm: state: dict of {substate_key';substate_value }
        @true if all prerequisities are satisifed by the passed states
        """
        sat = []
        for p_key, prereqObj in self.prereqs.items():
            if state is None:
                sat.append(None)
                break
            elif p_key in state.keys():
                reqObj =  self.prereqs[p_key]
                isSat = reqObj( state[p_key] )
                sat.append(isSat)
            else: 
                sat.append(False) # key not in state, can't be satisifed
        return all(sat)
        #return all(prereq(state[k]) for k, prereq in self.prereqs.items())

    def cost(self):
        return self._cost

    def expected_state(self, state):
        return expected_state(state, self.updates, self.dist)

    def outcomes(self, state):
        return outcome_dist(state, self.updates, self.dist)


class Goal(Action):
    """a goal that can timeout and fail"""
    def __init__(self, name, prereqs, outcomes, failures=None, time=None, repeats=False):
        super().__init__(name, prereqs, outcomes)
        self._time = time
        self.time = time
        self.repeats = repeats

        if failures is None:
            failures = ([{}], [1.])
        self.fail_updates, self.fail_dist = failures

    def __repr__(self):
        return 'Goal({})'.format(self.name)

    def tick(self):
        if self.time is not None:
            self.time -= 1

    def fail(self, state):
        """fail to complete this goal, returning the resulting state"""
        return resolve_outcomes(state, self.fail_updates, self.fail_dist)

    def reset(self):
        self.time = self._time

    def expected_failure_state(self, state):
        return expected_state(state, self.fail_updates, self.fail_dist)
