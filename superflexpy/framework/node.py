"""
Copyright 2019 Marco Dal Molin et al.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file is part of the SuperflexPy modelling framework. For details about it,
visit the page https://superflexpy.readthedocs.io

CODED BY: Marco Dal Molin
DESIGNED BY: Marco Dal Molin, Fabrizio Fenicia

This file contains the implementation of the Node class.
"""

from copy import copy, deepcopy
from ..utils.generic_component import GenericComponent


class Node(GenericComponent):
    """
    This class defines a Node. A node can be part of a network and it is a
    collection of Units. It's task is to sum the outputs of the Units,
    applying, if present, a routing.
    """
    def __init__(self, units, weights, area, id, shared_parameters=True):
        """
        This is the initializer of the class Node.

        Parameters
        ----------
        units : list(superflexpy.framework.unit.Unit)
            List of Units contained in the Node.
        weights : list
            List of weights to be applied to the Units when putting together
            their outputs. The order must be the same used in the units list.
            If a weight is a list, then different fluxes coming from the same
            unit have a different weight.
        area : float
            Influence area of the node. It is the net value: if a node has
            other nodes upstream, their area is not counted.
        id : str
            Identifier of the node. All the nodes of the framework must have an
            identifier.
        shared_parameters : bool
            True if the parameters of the Units are shared among the different
            Nodes.
        """

        self.id = id

        self._error_message = 'module : superflexPy, Node : {},'.format(id)
        self._error_message += ' Error message : '

        self._content = []
        for h in units:
            if shared_parameters:
                self._content.append(copy(h))
            else:
                self._content.append(deepcopy(h))
                self.add_prefix_parameters(id)

        self.area = area
        self._content_pointer = {hru.id: i
                                 for i, hru in enumerate(self._content)}
        self._weights = deepcopy(weights)
        self.add_prefix_states(id)

    # METHODS FOR THE USER

    def set_input(self, input):
        """
        This method sets the inputs to the node.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List of input fluxes.
        """

        self.input = input

    def get_output(self, solve=True):
        """
        This method solves the Node, solving each Unit and putting together
        their outputs according to the weight.

        Parameters
        ----------
        solve : bool
            True if the elements have to be solved (i.e. calculate the states).

        Returns
        -------
        list(numpy.ndarray)
            List containig the output fluxes of the node.
        """

        # Set the inputs
        for h in self._content:
            h.set_input(deepcopy(self.input))

        # Calculate output
        if isinstance(self._weights[0], float):
            for i, (h, w) in enumerate(zip(self._content, self._weights)):
                loc_out = h.get_output(solve)

                if i == 0:
                    output = [o * w for o in loc_out]
                else:
                    for j in range(len(output)):
                        output[j] += loc_out[j] * w
        else:
            for i, (h, w) in enumerate(zip(self._content, self._weights)):
                loc_out = h.get_output(solve)
                out_count = 0

                if i == 0:
                    output = []
                    for j in range(len(w)):
                        if w[j] is None:
                            output.append(0)
                        else:
                            output.append(loc_out[out_count] * w[j])
                            out_count += 1
                else:
                    for j in range(len(w)):
                        if w[j] is None:
                            continue
                        else:
                            output[j] += loc_out[out_count] * w[j]
                            out_count += 1

        return self._internal_routing(output)

    def get_internal(self, id, attribute):
        """
        This method allows to inspect attributes of the objects that belong to
        the node.

        Parameters
        ----------
        id : str
            Id of the object. If it is not a unit, it must contain the ids of
            the object containing it. If, for example it is an element, the id
            will be idUnit_idElement.
        attribute : str
            Name of the attribute to expose.

        Returns
        -------
        Unknown
            Attribute exposed
        """

        hru_num, ele = self._find_attribute_from_name(id)

        if ele:
            return self._content[hru_num].get_internal(id, attribute)
        else:
            try:
                method = getattr(self._content[hru_num], attribute)
                return method
            except AttributeError:
                message = '{}the attribute {} does not exist.'.format(self._error_message, attribute)
                raise AttributeError(message)

    def call_internal(self, id, method, **kwargs):
        """
        This method allows to call methods of the objects that belong to the
        node.

        Parameters
        ----------
        id : str
            Id of the object. If it is not a unit, it must contain the ids of
            the object containing it. If, for example it is an element, the id
            will be idUnit_idElement.
        method : str
            Name of the method to call.

        Returns
        -------
        Unknown
            Output of the called method.
        """
        hru_num, ele = self._find_attribute_from_name(id)

        if ele:
            return self._content[hru_num].call_internal(id, method, **kwargs)
        else:
            try:
                method = getattr(self._content[hru_num], method)
                return method(**kwargs)
            except AttributeError:
                message = '{}the method {} does not exist.'.format(self._error_message, method)
                raise AttributeError(message)

    # METHODS USED BY THE FRAMEWORK

    def add_prefix_parameters(self, id):
        """
        This method adds the prefix to the parameters of the elements that are
        contained in the node.

        Parameters
        ----------
        id : str
            Prefix to add.
        """

        for h in self._content:
            h.add_prefix_parameters(id)

    def add_prefix_states(self, id):
        """
        This method adds the prefix to the states of the elements that are
        contained in the node.

        Parameters
        ----------
        id : str
            Prefix to add.
        """

        for h in self._content:
            h.add_prefix_states(id)

    def external_routing(self, flux):
        """
        This methods applies the external routing to the fluxes. External
        routing is the one that affects the fluxes moving from the outflow of
        this node to the outflow of the one downstream. This function is used
        by the Network.

        Parameters
        ----------
        flux : list(numpy.ndarray)
            List of fluxes on which the routing has to be applied.
        """

        # No routing
        return flux

    # PROTECTED METHODS

    def _find_attribute_from_name(self, id):
        """
        This method is used to find the attributes or methods of the components
        contained for post-run inspection.

        Parameters
        ----------
        id : str
            Identifier of the component

        Returns
        -------
        int, bool
            Index of the component to look for and indication if it is an
            element (True) or not.
        """

        splitted = id.split('_')

        hru_num = self._find_content_from_name(id)

        if len(splitted) == 3:
            return (hru_num, True)  # We are looking for an element
        else:
            return (hru_num, False)

    def _internal_routing(self, flux):
        """
        Internal routing is the one that affects the flux coming to the Units
        and reaching the outflow of the node. This function is internally
        used by the node.
        """

        # No routing
        return flux

    # MAGIC METHODS

    def __copy__(self):
        message = '{}A Node cannot be copied'.format(self._error_message)
        raise AttributeError(message)

    def __deepcopy__(self, memo):
        message = '{}A Node cannot be copied'.format(self._error_message)
        raise AttributeError(message)

    def __repr__(self):
        str = 'Module: superflexPy\nNode: {}\n'.format(self.id)
        str += 'Units:\n'
        str += '\t{}\n'.format([h.id for h in self._content])
        str += 'Weights:\n'
        str += '\t{}\n'.format(self._weights)

        for h in self._content:
            str += '********************\n'
            str += '********************\n'
            str += h.__repr__()
            str += '\n'

        return str
