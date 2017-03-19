import math
from .base import Agent
from .utility import state_utility, change_utility, goals_utility
from functools import partial


class Planner():

    def __init__(self, succ_func, util_func):
        self.succ_func = succ_func
        self.util_func = util_func

    def heuristic(self, node, goal):
        """an admissible heuristic never overestimates the distance to the goal"""
        # override this with a better heuristic
        return 0

    def distance(self, from_node, to_node, action):
        """we define distance so that we minimize cost
        and maximize expected utility, but prioritize expected utility"""
        from_state, _ = from_node
        to_state, _ = to_node
        cost = action.cost()
        util = self.util_func(from_state, to_state)
        if util < 0:
            return cost * pow(util, 2)
        else:
            return cost * 0.1 * (math.tanh(-util) + 1)

    def _ida(self, agent, path, goal, length, depth, seen):
        """subroutine for iterative deepening A*. Returns
        @returns tuple of (min-distance-found,"""
        _, node = path[-1]

        f = length + self.heuristic(node, goal)
        if f > depth: return f, None

        state, _ = node
        if goal.satisfied(state):
            return f, path

        # extended list filtering:
        # skip nodes we have already seen
        nhash = hash(frozenset(node.items()))
        if nhash in seen: return f, None
        seen.add(nhash)

        minimum = float('inf')
        best_path = None
        for action, child in self.succ_func(node):
            # g(n) = distance(n)
            thresh, new_path = self._ida(agent,
                                         path + [(action, child)],
                                         goal,
                                         length + self.distance(node, child, action),
                                         depth, seen)
            if new_path is not None and thresh < minimum:
                minimum = thresh
                best_path = new_path
        return minimum, best_path

    def ida(self, agent, root, goal):
        """iterative deepening A*"""
        solution = None
        depth = self.heuristic(root, goal)
        while solution is None:
            _, solution = self._ida(agent, [(None, root)], goal, 0, depth, set())
            depth += 1
        return solution


def hill_climbing(root, succ_func, valid_func, depth):
    """always choose the best node next.
    this only terminates if the succ_func eventually returns nothing.
    assumes the succ_func returns child nodes in descending order of value.
    this may not find the highest-scoring path (since it's possible that the highest-scoring path
    goes through a low-scoring node), but this saves _a lot_ of time"""
    new_goals = set()
    seen = set()
    fringe = [[root]]
    while fringe:
        path = fringe.pop(0)
        node = path[-1]
        act, (state, goals) = node

        # extended list filtering:
        # skip nodes we have already seen
        nhash = hash(frozenset(state.items()))
        if nhash in seen: continue
        seen.add(nhash)

        # check that the next move is valid,
        # given the past node,
        # if not, save as a goal and backtrack
        if len(path) >= 2 and not valid_func(node, path[-2]):
            new_goals.add(act)
            continue

        # if we terminate at a certain depth, break when we reach it
        if depth is not None and len(path) > depth:
            break

        succs = succ_func(node)
        # if no more successors, we're done
        if not succs:
            break

        # assumed that these are best-ordered successors
        fringe = [path + [succ] for succ in succs] + fringe

    # remove the root
    path.pop(0)
    return path, new_goals


class PlanningAgent(Agent):
    """An (expected) utility maximizing agent,
    capable of managing long-term goals.
    @param state: starting state of the agent.
    @param actions: list of Action objects
    @param goal: list of Goal objects
    @param dict of  utility functions"""
    def __init__(self, state, actions, goals, utility_funcs):
        super().__init__(state)
        self.goals = set(goals)
        self.actions = actions
        self.ufuncs = utility_funcs
        self.utility = partial(state_utility, self.ufuncs)
        self.planner = Planner(self._succ_func, self.utility)

    def actions_for_state(self, state):
        """the agent's possible actions
        for a given agent state -
        you probably want to override this"""
        for action in self.actions:
            yield action

    def successors(self, state, goals):
        """the agent's possible successors (expected states)
        for a given agent state"""
        # compute expected states
        succs = []
        for action in self.actions_for_state(state):
            expstate = self._expected_state(action, state)
            succs.append((action, (expstate, goals)))

        for goal in goals:
            if goal.satisfied(state):
                expstate = self._expected_state(goal, state)
                remaining_goals = goals.copy()
                remaining_goals.remove(goal)
                succs.append((goal, (expstate, remaining_goals)))

        # sort by expected utility, desc
        succs = sorted(succs,
                       key=lambda s: self._score_successor(state, s[1][0]),
                       reverse=True)
        return succs

    def _score_successor(self, from_state, to_state):
        """score a successor based how it changes from the previous state"""
        chutil = change_utility(self.ufuncs, from_state, to_state)
        goutil = goals_utility(self.ufuncs, to_state, self.goals)
        return chutil + goutil

    def subplan(self, state, goal):
        """create a subplan to achieve a goal;
        i.e. the prerequisites for an action"""
        return self.planner.ida(self, state, goal.as_action())

    def _succ_func(self, node):
        """for planning; returns successors"""
        act, (state, goals) = node
        return self.successors(state, goals)

    def _valid_func(self, node, pnode):
        """for planning; checks if an action is possible"""
        act, (_, _) = node
        _, (state, _) = pnode
        return act.satisfied(state)

    def plan(self, state, goals, depth=None):
        """generate a plan; uses hill climbing search to minimize searching time.
        will generate new goals for actions which are impossible given the current state but desired"""
        plan, goals = hill_climbing((None, (state, self.goals)), self._succ_func, self._valid_func, depth)
        self.goals = self.goals | goals
        return plan, self.goals

    def _expected_state(self, action, state):
        """computes expected state for an action/goal,
        attenuating it if necessary"""
        return action.expected_state(state)
