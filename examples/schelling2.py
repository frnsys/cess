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
        self.width = width
        self.height = height

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
        prev_pos = yield from agent.get('pos')
        if prev_pos is not None:
            self.space.node[prev_pos] = {'agent': None}
        self.space.node[pos] = {'agent': agent}
        yield from agent.set(pos=pos)

    @asyncio.coroutine
    def compute_satisfaction(self, agent):
        type, similar, pos = yield from agent.get('type', 'similar', 'pos')
        neighbors = [n for n in self.neighbors(pos) if n['agent'] is not None]
        if neighbors:
            similars = []
            for n in neighbors:
                type_ = yield from n['agent'].get('type')
                if type_ == type:
                    similars.append(n)
            satisfied = len(similars)/len(neighbors) >= similar
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
        #print('{:.2f}% satisfied'.format(p_satisfied * 100))

    def printG(self):
      
        def printGrid(agents, xSize,ySize, cDefault='X', cErr='x'):
            """ turns agent data into a group of lines
            @reutrns list of y itesm, each x char long"""
            lines = []
            headerLine = ['-' for i in range(0,ySize)]
            lines.append(''.join(headerLine))
            for x in range(0, xSize):
                line = []
                for y in range(0,ySize):
                    ag = agents[(x*ySize)+ y]
                    if ag and ag._state:
                        line.append(str(ag._state.get('type',cDefault)) )
                    else:
                        line.append(cErr)

                lines.append(''.join(line))
            lines.append(''.join(headerLine))
            return lines


        nodeList = self.space.nodes
        rawAgents = [ x[1].get('agent',None) for x in self.space.nodes(data=True)]
        #nodes returns [(x,y),<agentDict>]

        lines = printGrid(rawAgents, self.width, self.height)
        for l in lines:
            print(l)
        return lines
 

if __name__ == '__main__':
    n_agents = 350 
    similar = 0.8
    types = [0,1]
    xSize = 20
    ySize = 20
    agents = [SchellingAgent(similar, random.choice(types)) for _ in range(n_agents)]
    sim = SchellingSim(agents, xSize, ySize)
    
    oldGrid = sim.printG()
    n_steps = 200
    sim.run(n_steps)
    newGrid = sim.printG()

    for i in range(0, ySize):
        print(oldGrid[i] + ' ' + newGrid[i])

