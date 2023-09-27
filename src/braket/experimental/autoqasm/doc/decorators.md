# AutoQASM decorators

AutoQASM function decorators are special wrapper objects that allow us to override the normal behavior of the wrapped code. This is how we are able to hook into normal python control flow statements add them to the quantum program within our wrapped functions, for instance.

There are a handful of decorators available through AutoQASM. Each one may attach its own special behaviors to the function it wraps. If you are new to AutoQASM, you can just use `@aq.main`! The other decorators unlock further capabilities, when you need it.

## `@aq.main`

This decorator marks the entry point to a quantum program.

You can include gates and pulse control, classical control and subroutine calls. When you call the function wrapped by `@aq.main`, you will get a `Program` object. The `Program` object can execute on Braket devices. The code snippet below creates a quantum program with `@aq.main` and runs it on the `AwsDevice` instantiated as `device`.

```
@aq.main(num_qubits=5)
def ghz_state(max_qubits):
    """Create a GHZ state from a variable number of qubits."""
    h(0)
    for i in aq.range(max_qubits):
        cnot(0, i)
    measure(list(range(max_qubits))) 
    
ghz_state_program = ghz_state(max_qubits=5)

device.run(ghz_state_program)
```

When you run your quantum program, the Amazon Braket SDK automatically serializes the program to OpenQASM before sending it to the Amazon Braket service. In AutoQASM, you can optionally view the OpenQASM script of your quantum program before submitting to a device.

```
print(ghz_state_program.to_ir())
```

## `@aq.subroutine`

This decorator declares a function to be a quantum program subroutine.

Like any subroutine, `@aq.subroutine` is often used to simplify repeated code and increase the readability of a program, and it must be called at least once to have an effect.

AutoQASM must support typed serialization formats, and so you must provide type hints for the inputs of your subroutine definitions. Qubits are like global registers to our quantum computation, so virtual qubits used in the body of a subroutine definition must be passed as input arguments. 

Our example below uses a subroutine to make two bell states.
```
@aq.subroutine
def bell(q0: int, q1: int) -> None:
    h(q0)
    cnot(q0, q1)

    
@aq.main(num_qubits=4)
def two_bell() -> None:
    bell(0, 1)
    bell(2, 3)

two_bell_program = two_bell()
```

Let's take a look at the serialized output from `two_bell_program.to_ir()`, which shows that the modularity of the subroutine is preserved.

```
OPENQASM 3.0;
def bell(int[32] q0, int[32] q1) {
    h __qubits__[q0];
    cnot __qubits__[q0], __qubits__[q1];
}
qubit[4] __qubits__;
bell(0, 1);
bell(2, 3);
```

## `@aq.gate`

Represents a gate definition.

Gate definitions define higher-level gates with support gates, and are often used to decompose a gate into the native gates of a device.

The body of a gate definition can only contain gates. Qubits used in the body of a gate definition must be passed as input arguments, with the type hint `aq.Qubit`. Like subroutines, a gate must be called by a main quantum program to have an effect.

```
@aq.gate
def ch(q0: aq.Qubit, q1: aq.Qubit):
    """Define a controlled-Hadamard gate."""
    ry(q1, -math.pi / 4)
    cz(q0, q1)
    ry(q1, math.pi / 4)
    
@aq.main(num_qubits=2)
def main():
    h(0)
    ch(0, 1)
    
main_program = main()
```


## `@aq.gate_calibration`

This decorator allows you to register a calibration for a gate. A gate calibration is a device-specific, low-level, pulse implementation for a logical gate operation.

At the pulse level, qubits are no longer interchangable. Each one has unique properties. Thus, a gate calibration is usually defined for a concrete set of qubits and parameters, but you can use input arguments to your function as well.

The body of a gate calibration must only contain pulse operations. This decorator requires one input arguments to specify the `Gate` that the calibration will be registered to. Concrete values for the qubits and parameters are supplied as keyword arguments to the decorator.
The union of the arguments of the decorator and the decorated function must match the arguments of the gate to be implemented.

For example, the gate `rx` takes two arguments, target and angle. Each arguments must be either set in the decorator or declared as an input parameter to the decorated function. To add the gate calibration to your program, use the `with_calibrations` method of the main program.

```
# This calibration only applies to physical qubit zero, so we
# mark that in the decorator call
@aq.gate_calibration(implements=rx, target="$0")
def cal_1(angle: float):
    # The calibration is applicable for any rotation angle,
    # so we accept it as an input argument
    pulse.barrier("$0")
    pulse.shift_frequency(q0_rf_frame, -321047.14178613486)
    pulse.play(q0_rf_frame, waveform(angle))
    pulse.shift_frequency(q0_rf_frame, 321047.14178613486)
    pulse.barrier("$0")
    
@aq.main
def my_program():
    rx(0, 0.123)
    measure(0)
```