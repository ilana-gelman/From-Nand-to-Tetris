"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

CLASS_SCOPE_KIND = {'STATIC', 'FIELD'}
METHOD_SCOPE_KIND = {'VAR', 'ARG'}  # var -> local
PRIMITIVE_TYPES = {'int', 'char', 'boolean'}
GET_TYPE = 0
GET_KIND = 1
GET_INDEX = 2

class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        # Your code goes here!
        self.occasions_counter = {'STATIC': 0, 'FIELD': 0, 'VAR': 0, 'ARG': 0}
        self.class_scope = dict()  # { 'id'
        self.method_scope = None

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        # Your code goes here!
        self.method_scope = dict()
        self.occasions_counter['VAR'] = 0
        self.occasions_counter['ARG'] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        # Your code goes here!

        if kind in CLASS_SCOPE_KIND and name not in self.class_scope.keys():
            self.class_scope[name] = [type, kind, self.occasions_counter[kind]]
            self.occasions_counter[kind] = self.occasions_counter[kind] + 1

        elif kind in METHOD_SCOPE_KIND and name not in self.method_scope.keys():
            self.method_scope[name] = [type, kind, self.occasions_counter[kind]]
            self.occasions_counter[kind] = self.occasions_counter[kind] + 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        # Your code goes here!
        if kind in METHOD_SCOPE_KIND or kind in CLASS_SCOPE_KIND:
            return self.occasions_counter[kind]
        return -1

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        # Your code goes here!
        return self.get_value_by_index(name, GET_KIND)

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        # Your code goes here!
        return self.get_value_by_index(name, GET_TYPE)

    def get_value_by_index(self,name, index):
        if name in self.method_scope.keys():
            return self.method_scope[name][index]
        elif name in self.class_scope.keys():
            return self.class_scope[name][index]
        return ''

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        # Your code goes here!
        return self.get_value_by_index(name, GET_INDEX)
