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

"""Tests for the gates module."""

import braket.experimental.autoqasm as aq
from braket.experimental.autoqasm.gates import cnot, h, measure


def test_bell_state_prep(bell_state_program) -> None:
    """Tests Bell state generation without measurement."""
    expected = """OPENQASM 3.0;
qubit[2] __qubits__;
h __qubits__[0];
cnot __qubits__[0], __qubits__[1];"""
    actual_result = bell_state_program().to_ir()
    assert actual_result == expected


def test_physical_q_bell_state_prep(physical_bell_program) -> None:
    """Tests Bell state generation without measurement on particular qubits."""
    expected = """OPENQASM 3.0;
h $0;
cnot $0, $5;"""
    actual_result = physical_bell_program().to_ir()
    assert actual_result == expected


def test_bell_with_measure() -> None:
    """Tests Bell state with measurement result stored in an undeclared variable."""
    with aq.build_program() as program_conversion_context:
        h(0)
        cnot(0, 1)
        measure(0)
    expected = """OPENQASM 3.0;
h __qubits__[0];
cnot __qubits__[0], __qubits__[1];
bit __bit_0__;
__bit_0__ = measure __qubits__[0];"""

    qasm = program_conversion_context.make_program().to_ir()
    assert qasm == expected.strip()