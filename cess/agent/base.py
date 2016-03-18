import asyncio
from uuid import uuid4
from .state import attenuate_state, attenuate_value


class Agent():
    """a basic agent"""
    def __init__(self, state=None, constraints=None):
        self.id = uuid4().hex
        self._state = state or {}
        self.constraints = constraints or {}

    def __setitem__(self, key, val):
        """set a state value, attenuating if necessary"""
        if key in self.constraints:
            val = attenuate_value(val, self.constraints[key])
        self._state[key] = val

    @asyncio.coroutine
    def __getitem__(self, key):
        """retrieves a state value;
        a coroutine for remote access"""
        return self._state[key]

    def attenuate(self, state):
        """attenuate a given state to fit within constraints"""
        return attenuate_state(state, self.constraints)

    @property
    def state(self):
        """return a copy of the state"""
        return self._state.copy()

    @state.setter
    def state(self, state):
        """set the entire state at once,
        attenuating as necessary"""
        self._state = self.attenuate(state)

    @asyncio.coroutine
    def call(self, fname, *args, **kwargs):
        """call a method on the agent.
        if another agent needs access to a method, use this method,
        since it supports remote access"""
        return getattr(self, fname)(*args, **kwargs)

    @asyncio.coroutine
    def request(self, propname):
        """get a property from the agent.
        if another agent needs access to a property, use this method,
        sicne it supports remote access"""
        if isinstance(propname, list):
            return [getattr(self, p) for p in propname]
        else:
            return getattr(self, propname)

    def step(self, world):
        raise NotImplementedError


class AgentProxy():
    """an agent proxy represents an agent that is accessed remotely"""
    # the worker the agent belongs to,
    # assigned when agents are distributed
    worker = None

    def __init__(self, agent):
        self.id = agent.id

    @asyncio.coroutine
    def __getitem__(self, key):
        return (yield from self.worker.query_agent({
            'id': self.id,
            'key': key
        }))

    @asyncio.coroutine
    def call(self, fname, *args, **kwargs):
        return (yield from self.worker.call_agent({
            'id': self.id,
            'func': fname,
            'args': args,
            'kwargs': kwargs
        }))

    @asyncio.coroutine
    def request(self, propname):
        return (yield from self.worker.call_agent({
            'id': self.id,
            'func': 'request',
            'args': (propname,)
        }))

    def __repr__(self):
        return 'AgentProxy({})'.format(self.id)
