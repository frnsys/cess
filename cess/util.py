import random


def random_choice(choices):
    """returns a random choice
    from a list of (choice, probability)"""
    # sort by probability
    choices = sorted(choices, key=lambda x:x[1])
    roll = random.random()

    acc_prob = 0
    for choice, prob in choices:
        acc_prob += prob
        if roll <= acc_prob:
            return choice


def shuffle(l):
    random.shuffle(l)
    return l


def ewma(p_mean, val, alpha=0.8):
    """computes exponentially weighted moving mean"""
    return p_mean + (alpha * (val - p_mean))


def hyperbolic_discount(value, days, k):
    discount = 1/(1+days*k)
    return discount * value
