import asyncio
from uuid import uuid4


class Agent():
    """A very 'basic agent'. 
    Mostly a wrapper for a dict indicting current state.
    dict it key/value pairs. Usually 'string';[int|lfoat] 
    """

    # workaround for <https://github.com/uqfoundation/dill/issues/75>
    # instead of using `super()`, use `self._super(Subclass, self)`
    _super = super

    def __init__(self, state=None):
        self.id = uuid4().hex
        self.type = type(self)
        self._state = state or {}

    def __setitem__(self, key, val):
        """set a state value;
        this is only available for a local agent (not an AgentProxy)"""
        self._state[key] = val

    def __getitem__(self, keys):
        """get a state value;
        this is only available for a local agent (not an AgentProxy)"""
        if isinstance(keys, str):
            return self._state[keys]
        return [self._state[k] for k in keys]

    @asyncio.coroutine
    def get(self, *keys):
        """retrieves a state value; a coroutine for remote access"
        @returns single value for one key
        @returns if more than one 'key' specified, a dict is returned
        """
        if len(keys) == 1:
            return self._state[keys[0]]
        return [self._state[k] for k in keys]

    @asyncio.coroutine
    def set(self, **kwargs):
        """set one or more state variables
        Expected is an args=key value to set list """
        #TRICKY: list is not checked before applying 
        self._state.update(kwargs)

    @asyncio.coroutine
    def call(self, fname, *args, **kwargs):
        """call a method on the agent.
        if another agent needs access to a method, use this method,
        since it supports remote access"""
        return getattr(self, fname)(*args, **kwargs)


class AgentProxy():
    """an agent proxy represents an agent that is accessed remotely.
    Includes internal worker thread"""

    # the worker the agent belongs to,
    # assigned when agents are distributed
    worker = None

    def __init__(self, agent):
        self.id = agent.id
        self.type = type(agent)

    @asyncio.coroutine
    def get(self, *keys):
        return (yield from self.worker.call_agent({
            'id': self.id,
            'func': 'get',
            'args': keys
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
    def set(self, **kwargs):
        return (yield from self.worker.call_agent({
            'id': self.id,
            'func': 'set',
            'kwargs': kwargs
        }))

    def __repr__(self):
        return 'AgentProxy({}, {})'.format(self.id, self.type.__name__)

    def __eq__(self, other):
        return self.id == other.id
