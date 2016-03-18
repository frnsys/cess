import random


class QLearner():
    def __init__(self, states_actions, rewards, discount=0.5, explore=0.0, learning_rate=0.5):
        """basic Q-learning. given an environment where actions result in uncertain states,
        Q-learning allows the agent to learn a policy (that is, the best action to take given a state).

        - states_actions: a mapping of states to viable actions for that state
        - rewards: a reward function, taking a state as input, or a mapping of states to a reward value
        - discount: how much the agent values future rewards over immediate rewards
        - explore: with what probability the agent "explores", i.e. chooses a random action
        - learning_rate: how quickly the agent learns
        """
        self.discount = discount
        self.explore = explore
        self.learning_rate = learning_rate
        self.R = rewards.get if isinstance(rewards, dict) else rewards

        # previous (state, action)
        self.prev = (None, None)

        # initialize Q
        self.Q = {}
        for state, actions in states_actions.items():
            self.Q[state] = {a:0 for a in actions}

    def choose_action(self, state):
        """choose an action to take"""
        if random.random() < self.explore:
            action = random.choice(list(self.Q[state].keys()))
        else:
            action = self._best_action(state)

        # learn from the previous action, if there was one
        self._learn(state)

        # remember this state and action
        self.prev = (state, action)

        return action

    def _best_action(self, state):
        """choose the best action given a state"""
        actions_rewards = list(self.Q[state].items())
        return max(actions_rewards, key=lambda x: x[1])[0]

    def _learn(self, state):
        """update Q-value for the last taken action"""
        p_state, p_action = self.prev
        if p_state is None:
            return
        self.Q[p_state][p_action] = self.learning_rate * (self.R(state) + self.discount * max(self.Q[state].values())) - self.Q[p_state][p_action]
