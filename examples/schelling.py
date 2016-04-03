"""
schelling's model of segregation.

this is an example of a model that is best run on a single node -
each agent does not really do much computation on its own, so the
overhead of coordinating distributed agents is not worth it.
"""

import random
import asyncio
import networkx as nx
from cess import Simulation, Agent


class SchellingAgent(Agent):
    def __init__(self, similar, type):
        self._super(SchellingAgent, self).__init__(state={
            'similar': similar,
            'type': type,
            'pos': None
        })


class SchellingSim(Simulation):
    def __init__(self, agents, width, height):
        super().__init__(agents)

        if len(agents) > width * height:
            raise Exception('there must be enough space for all agents')

        # seutp grid
        self.space = nx.grid_2d_graph(width, height)

        # place agents
        positions = self.space.nodes()
        random.shuffle(positions)
        for agent in self.agents:
            pos = positions.pop()
            self.sync(self.place(agent, pos))

        # setup vacant positions
        for pos in positions:
            self.space.node[pos] = {'agent': None}

    def neighbors(self, pos):
        return [self.space.node[n] for n in self.space.neighbors(pos)]

    @asyncio.coroutine
    def place(self, agent, pos):
        prev_pos = yield from agent['pos']
        if prev_pos is not None:
            self.space.node[prev_pos] = {'agent': None}
        self.space.node[pos] = {'agent': agent}
        yield from agent.set(pos=pos)

    @asyncio.coroutine
    def compute_satisfaction(self, agent):
        state = yield from agent['type', 'similar', 'pos']
        neighbors = [n for n in self.neighbors(state['pos']) if n['agent'] is not None]
        if neighbors:
            similar = []
            for n in neighbors:
                type = yield from n['agent']['type']
                if type == state['type']:
                    similar.append(n)
            satisfied = len(similar)/len(neighbors) >= state['similar']
        else:
            satisfied = True
        return satisfied

    @asyncio.coroutine
    def update_agent(self, agent):
        satisfied = yield from self.compute_satisfaction(agent)
        if not satisfied:
            vacancies = [pos for pos, data in self.space.node.items() if data['agent'] is None]
            pos = random.choice(vacancies)
            yield from self.place(agent, pos)
        return (yield from self.compute_satisfaction(agent))

    @asyncio.coroutine
    def step(self):
        statuses = []
        for agent in self.agents:
            satisfied = yield from self.update_agent(agent)
            statuses.append(satisfied)
        p_satisfied = len([s for s in statuses if s])/len(self.agents)
        print('{:.2f}% satisfied'.format(p_satisfied * 100))


if __name__ == '__main__':
    n_agents = 2200
    similar = 0.8
    types = [0,1]
    agents = [SchellingAgent(similar, random.choice(types)) for _ in range(n_agents)]
    sim = SchellingSim(agents, 50, 50)

    n_steps = 100
    sim.run(n_steps)
