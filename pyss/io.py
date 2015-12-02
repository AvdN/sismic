import yaml
from pyss.statemachine import Event, Transition, StateMachine, BasicState, CompoundState, OrthogonalState, HistoryState, FinalState
from pyss.statemachine import StateMixin, ActionStateMixin, TransitionStateMixin, CompositeStateMixin


def import_from_yaml(data):
    """
    Import a state machine from a YAML representation.
    :param data: string or any equivalent object
    :return: a StateMachine instance
    """
    return import_from_dict(yaml.load(data)['statemachine'])


def import_from_dict(data: dict):
    """
    Import a state machine from a (set of nested) dictionary.
    :param data: dict-like structure
    :return: a StateMachine instance
    """
    sm = StateMachine(data['name'], data['initial'], data.get('on entry', None))

    states_to_add = []  # list of (state, parent) to be added
    for state in data['states']:
        states_to_add.append((state, None))

    # Add states
    while states_to_add:
        state_d, parent_name = states_to_add.pop()

        # Create and register state
        # TODO: Catch exception and provide details about the "parsing" error
        state = _state_from_dict(state_d)
        sm.register_state(state, parent_name)

        # Register transitions if any
        for transition_d in state_d.get('transitions', []):
            # TODO: Catch exception and provide details about the "parsing" error
            transition = _transition_from_dict(state.name, transition_d)
            sm.register_transition(transition)

        # Register substates
        for substate in state_d.get('states', []):
            states_to_add.append((substate, state.name))

    return sm


def _transition_from_dict(state_name: str, transition_d: dict):
    """
    Return a Transition instance from given dict.
    :param state: name of the state in which the transition is defined
    :param transition_d: a dictionary containing transition data
    :return: an instance of Transition
    """
    to_state = transition_d.get('target', None)
    event = transition_d.get('event', None)
    if event:
        event = Event(event)
    condition = transition_d.get('guard', None)
    action = transition_d.get('action', None)
    return Transition(state_name, to_state, event, condition, action)


def _state_from_dict(state_d: dict):
    """
    Return the appropriate type of state from given dict.
    :param state_d: a dictionary containing state data
    :return: a specialized instance of State
    """
    # Guess the type of state
    if state_d.get('type', None) == 'final':
        # Final pseudo state
        state = FinalState(state_d['name'])
    elif state_d.get('type', None) == 'history':
        # History pseudo state
        state = HistoryState(state_d['name'], state_d.get('initial'), state_d.get('deep', False))
    else:
        name = state_d.get('name')
        on_entry = state_d.get('on entry', None)
        on_exit = state_d.get('on exit', None)
        if 'states' in state_d:  # Compound state
            initial = state_d['initial']
            state = CompoundState(name, initial, on_entry, on_exit)
        elif 'orthogonal states' in state_d: #
            state = OrthogonalState(name, on_entry, on_exit)
        else:
            # Simple state
            state = BasicState(name, on_entry, on_exit)
    return state
