import math
import asyncio
from cess import Agent


class Person(Agent):
    def __init__(self):
        self._super(Person, self).__init__(state={
            'employer': None,
            'wage': 0,
            'cash': 5000,
            'frugality': 0,
            'goods': 0
        })

    @asyncio.coroutine
    def quit(self):
        self['employer'] = None
        self['wage'] = 0

    @asyncio.coroutine
    def hire(self, employer, wage):
        self['employer'] = employer
        self['wage'] = wage

    def consumption(self, price):
        i = 0
        while self.marginal_utility(price, i) > 0:
            i += 1
        return i

    def marginal_utility(self, price, n_goods):
        return round(self.cash_change_utility(-price)
                   + self.consumer_good_utility_change(n_goods), 4)

    def consumer_good_utility_change(self, n_goods):
        """marginal utility"""
        u = self.consumer_good_utility(n_goods)
        u_ = self.consumer_good_utility(n_goods + 1)
        return round(u_ - u, 4)

    def consumer_good_utility(self, n_goods):
        # sigmoid
        good_utility = 100
        return good_utility/(1 + math.exp(-n_goods)) - 0.5

    def cash_utility(self, cash):
        u = cash-1 if cash <= 0 else 400/(1 + math.exp(-cash/20000)) - (400/2) # sigmoid for cash > 0, linear otherwise
        return u * math.sqrt(1.1 + self['frugality'])

    def cash_change_utility(self, change):
        return self.cash_utility(self['cash'] + change) - self.cash_utility(self['cash'])

    @asyncio.coroutine
    def purchase_goods(self, supplier):
        price, supply = yield from supplier.get('price', 'supply')
        desired_goods = max(0, (self.consumption(price)) - self['goods'])

        if not price:
            to_purchase = desired_goods
        else:
            can_afford = max(0,  math.floor(self['cash']/price))
            desired_goods = min(can_afford, desired_goods)
            to_purchase = min(desired_goods, supply)
        cost = to_purchase * price
        self['cash'] -= cost
        yield from supplier.call('sell', to_purchase)
        self['goods'] += to_purchase

        return desired_goods - to_purchase, to_purchase

    def consume(self):
        self['goods'] = 0
