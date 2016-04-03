import math
import asyncio
from cess import Simulation
from cess.util import shuffle, random_choice


class EconomySim(Simulation):
    def __init__(self, people, raw_material_firms, consumer_good_firms, capital_equipment_firms):
        self.people = people
        self.raw_material_firms = raw_material_firms
        self.consumer_good_firms = consumer_good_firms
        self.capital_equipment_firms = capital_equipment_firms
        self.firms = self.raw_material_firms + self.consumer_good_firms + self.capital_equipment_firms
        self.state = {
            'mean_wage': 10,
            'mean_equip_price': 10
        }
        super().__init__(people + self.firms)

    @asyncio.coroutine
    def step(self):
        tasks = [firm.call('set_production_target', self.state) for firm in shuffle(self.firms)]
        jobs = yield from asyncio.gather(*tasks)
        jobs = list(zip(jobs, self.firms))
        yield from self.labor_market(jobs)

        yield from asyncio.gather(*[firm.call('produce', self.state) for firm in self.raw_material_firms])

        # raw material market
        sold = yield from self.market(
            self.raw_material_firms,
            self.consumer_good_firms + self.capital_equipment_firms,
            'purchase_materials')
        print('materials: ${:.2f}'.format(self.mean_sales_price(sold)))

        yield from asyncio.gather(*[firm.call('produce', self.state) for firm in self.capital_equipment_firms])

        # capital equipment market
        sold = yield from self.market(
            self.capital_equipment_firms,
            self.consumer_good_firms + self.raw_material_firms,
            'purchase_equipment')
        print('equipment: ${:.2f}'.format(self.mean_sales_price(sold)))

        yield from asyncio.gather(*[firm.call('produce', self.state) for firm in self.consumer_good_firms])

        # consumer good market
        sold = yield from self.market(
            self.consumer_good_firms,
            self.people,
            'purchase_goods')
        print('consumer goods: ${:.2f}'.format(self.mean_sales_price(sold)))

        # people consume (reset) their goods
        yield from asyncio.gather(*[p.call('consume') for p in self.people])


    @asyncio.coroutine
    def labor_market(self, jobs):
        tasks = [p.get('employer') for p in self.people]
        applicants = {f: [] for (_, __), f in jobs}
        employers = yield from asyncio.gather(*tasks)
        job_seekers = [p for p, e in zip(self.people, employers) if e is None]
        while job_seekers and jobs:
            job_dist = self.job_distribution(jobs)
            for p in shuffle(job_seekers):
                (n_vacancies, wage), firm  = random_choice(job_dist)
                applicants[firm].append(p)

            # firms select from their applicants
            _jobs = []
            for job in shuffle(jobs):
                # filter down to valid applicants
                (n_vacancies, wage), firm = job
                apps = [a for a in applicants[firm] if a in job_seekers]
                hired, n_vacancies, wage = yield from firm.call('hire', apps, wage)

                # remove hired people from the job seeker pool
                for p in hired:
                    job_seekers.remove(p)

                if not job_seekers:
                    break

                # if vacancies remain, post the new jobs with the new wage
                if n_vacancies:
                    _jobs.append(((n_vacancies, wage), firm))
            jobs = _jobs

    @asyncio.coroutine
    def market(self, sellers, buyers, purchase_func):
        sold = []
        seller_dist = yield from self.firm_distribution(sellers)

        while buyers and seller_dist:
            for buyer in shuffle(buyers):
                supplier = random_choice(seller_dist)
                required, purchased = yield from buyer.call(purchase_func, supplier)
                supply, price = yield from supplier.get('supply', 'price')
                sold.append((purchased, price))
                if required == 0:
                    buyers.remove(buyer)

                # if supplier sold out, update firm distribution
                if supply == 0:
                    seller_dist = yield from self.firm_distribution(sellers)

                if not seller_dist:
                    break
        return sold

    @asyncio.coroutine
    def firm_distribution(self, firms):
        """computes a probability distribution over firms based on their prices.
        the lower the price, the more likely they are to be chosen"""
        tasks = [f.get('supply', 'price') for f in firms]
        vals = yield from asyncio.gather(*tasks)
        firms = [(f, price) for (supply, price), f in zip(vals, firms) if supply > 0]
        probs = [math.exp(-math.log(price)) if price > 0 else 1. for f, price in firms]
        mass = sum(probs)
        return [(f, p/mass) for (f, price), p in zip(firms, probs)]

    def job_distribution(self, jobs):
        """computes a probability distribution over jobs based on their wages.
        the higher the wage, the more likely they are to be chosen"""
        probs = [math.exp(-math.log(wage)) for (_, wage), __ in jobs]
        mass = sum(probs)
        return [(j, p/mass) for j, p in zip(jobs, probs)]

    def mean_sales_price(self, sold):
        sell_prices = []
        for amt, price in sold:
            sell_prices += [price for _ in range(amt)]
        return sum(sell_prices)/len(sell_prices) if sell_prices else 0
