from enum import Enum, unique


@unique
class SimulatedObjectStatus(Enum):
    """
    An enumeration for whether a simulated object has entered and
    possibly exited the network.
    """
    AWAITING_COMMAND_TO_ENTER = 10
    '''The time for the simulated object to enter the network has not yet arrived.'''
    QUEUED_TO_ENTER = 20
    '''The time for the simulated object to enter has arrived, but it has not entered yet.'''
    IN_NETWORK = 30
    '''The simulated object is active in the network.'''
    EXITED_NETWORK = 40
    '''The simulated object has exited the network.'''
