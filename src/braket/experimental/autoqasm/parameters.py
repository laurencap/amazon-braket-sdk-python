# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.


"""Non-unitary instructions that apply to qubits."""

from braket.circuits.free_parameter import FreeParameter
from braket.experimental.autoqasm.types import FloatVar, IntVar


class TypedParameter(FreeParameter):
    def __init__(self, name: str, type: type | None = float):
        """
        Initializes a new :class:'TypedParameter' object.

        Supports floats and integers.

        Args:
            name (str): Name of the :class:'TypedParameter'. Can be a unicode value.
            type (type): Optional type of the parameter, which defaults to float.

        Raises:
            ValueError: If the type is unsupported.

        Examples:
            >>> param1 = TypedParameter("theta")
            >>> param1 = TypedParameter("theta", float)
        """
        # Update if FreeParameter gains support for types
        if type not in [float, int, FloatVar, IntVar]:
            raise ValueError(f"Unsupported type for {self.__class__.__name__}: {type}.")
        # Note: We call super first, because FreeParameter doesn't accept a type, but
        # FreeParameterExpression does and sets it to a default value
        super().__init__(name=name)
        self._type = type

    @property
    def type(self) -> type:
        """
        type: Type of this parameter.
        """
        return self._type
