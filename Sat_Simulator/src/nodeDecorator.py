from typing import TYPE_CHECKING
from src.node import Node

if TYPE_CHECKING:
    from src.packet import Packet

class NodeDecorator (Node):
    """
    This class functions as a decorator object for the satellite class.
    Please use this object to add new functionality to a an already existing satellite object.
    """
    ##implements a decorator pattern for the satellite class
    def __init__(self, node: 'Node'):
        self._node = node
        

    def load_data(self, timeStep: 'float') -> None:
        pass

    def load_packet_buffer(self, packet:'Packet' = None ) -> None:
        pass

    def recieve_packet(self, pck: 'Packet') -> None:
        pass

    def __getattr__(self, name):
        if "_node" in self.__dict__.keys():
            return getattr(self._node, name)
        else:
            pass

    def __setattr__(self, name, value):
        if "_node" in self.__dict__.keys():
            setattr(self._node, name, value)
        else:
            self.__dict__[name] = value

    def __str__(self):
        return str(self._node)

    ##This method is normally used when the object is pickled
    def __setstate__(self, d):
        self.__dict__ = d
