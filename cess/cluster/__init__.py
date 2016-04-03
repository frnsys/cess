import asyncio
from .client import Client
from ..agent import Agent, AgentProxy


class Cluster(Client):
    def __init__(self, host, port):
        super().__init__(host, port)

    def submit(self, command, **data):
        """submit a command (and optionally data) to the arbiter (synchronous)"""
        data.update({'cmd': command})

        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(self.send_recv(data))
        for result in results:
            if 'exception' in result:
                print(result['traceback'])
        return results

    @asyncio.coroutine
    def call_agents(self, func, *args, **kwargs):
        return (yield from self.send_recv({
            'cmd': 'call_agents',
            'func': func,
            'args': args,
            'kwargs': kwargs
        }))

    @asyncio.coroutine
    def call_agent(self, data):
        d = {'args': [], 'kwargs': {}}
        d.update(data)
        d['cmd'] = 'call_agent'
        return (yield from self.send_recv(d))


def proxy_agents(agent):
    """recursively replace all Agent references in the agent to AgentProxy"""
    for k, v in agent.__dict__.items():
        if isinstance(v, list):
            setattr(agent, k, [AgentProxy(o) if isinstance(o, Agent) else o for o in v])
        elif isinstance(v, Agent):
            setattr(agent, k, AgentProxy(v))
        else:
            try:
                proxy_agents(v)
            except AttributeError:
                pass
