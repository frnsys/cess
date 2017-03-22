import asyncio
from .agent import AgentProxy
from .cluster import Cluster, proxy_agents


class Simulation():

    
    def __init__(self, agents):
        """a agent-based simulation"""
        self.agents = agents
        self.is_done = False

    def run(self, steps, arbiter=None):
        """run the simulation for a specified number of time steps.
        if you specify a connection tuple for `arbiter`, e.g. `('127.0.0.1', 8888)`,
        this will distribute the agents to the arbiter's cluster"""
        if arbiter is not None:
            # distribute agents across cluster
            for agent in self.agents:
                proxy_agents(agent)

            host, port = arbiter
            cluster = Cluster(host, port)
            cluster.submit('populate', agents=self.agents)

            _agents = []
            for agent in self.agents:
                proxy = AgentProxy(agent)
                proxy.worker = cluster
                _agents.append(proxy)
            self.agents = _agents

        loop = asyncio.get_event_loop()
        for _ in range(steps):
            if self.is_done :
                break
            loop.run_until_complete(self.step())

    @asyncio.coroutine
    def step(self):
        """run the simulation one time-step"""
        raise NotImplementedError

    def sync(self, coro):
        """run a coroutine synchronously"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(coro)

