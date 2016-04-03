"""
a simulation of a simple economy which includes q-learning agents.

based off of:

    An Agent-Based Model of a Minimal Economy. Christopher K. Chan. May 5, 2008.
    <http://eos.cs.princeton.edu/ChrisChan_IW_2008_Part2.pdf>
"""

from simulation import EconomySim
from person import Person
from firm import RawMaterialFirm, ConsumerGoodFirm, CapitalEquipmentFirm


if __name__ == '__main__':
    config = {
        'labor_cost_per_good': 10,
        'material_cost_per_good': 20,
        'labor_per_equipment': 50,
        'labor_per_worker': 200,
        'supply_increment': 10,
        'profit_increment': 2,
        'wage_increment': 1
    }
    people = [Person() for _ in range(100)]
    raw_material_firms = [RawMaterialFirm(**config) for _ in range(10)]
    capital_equipment_firms = [CapitalEquipmentFirm(**config) for _ in range(10)]
    consumer_good_firms = [ConsumerGoodFirm(**config) for _ in range(10)]
    sim = EconomySim(people, raw_material_firms, capital_equipment_firms, consumer_good_firms)

    n_steps = 100
    sim.run(n_steps)
