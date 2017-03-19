""" 
Contains tools for doing state updates
state variable is expected to be a dict
of key:value pairs that our are various state date.
"""

def update_state(state, update, expected=False):
    """Generates a new state based on the specified update dict;
    @updates: Dict of update function. value can be: constant (to add), or
     a function taking a 'state' dictionary 
    @returns copy of state with updated values.
    note: this does not attenuate (clamp) the state"""
    if state is not None:
        state = state.copy()
    
    if update is None:
        return state

    for k, v in update.items():

        # ignore keys not in state
        if k not in state:
            continue

        # get the type of the value
        # to coerce it back if necessary
        typ = type(state[k])

        # v can be a callable taking the state dict,
        # or an int/float
        try:
            val = v(state)
            if isinstance(val, tuple):
                val, exp = val
            else:
                exp = val
            state[k] = (exp if expected else val)
        except TypeError:
            state[k] += v
        state[k] = typ(state[k]) #set and coherse back
    return state


def attenuate_state(state, ranges):
    """attenuates a state so that its values are within the specified ranges
    edits value of passed states, and returns passed (updated) state
    @ranges dict of ranges 'key:range-obj'
    @state dict of states 'key:value'
    """
    for k, v in state.items():
        if k in ranges:
            state[k] = attenuate_value(v, ranges[k])
    return state


def attenuate_value(value, range):
    """attenuates (clamps) a value to be within the specified range"""
    mn, mx = range
    if mn is not None: value = max(mn, value)
    if mx is not None: value = min(mx, value)
    return value
