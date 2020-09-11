class Value(object):
    def __init__(self, value: str):
        value = value.upper()
        if value == 0 or value == '0':
            self.value = 0
        elif value == 1 or value == '1':
            self.value = 1
        else:
            self.value = 'U'

    def __eq__(self, other):
        if self.value == 1:
            if other == 1 or other == '1':
                return True
        elif self.value == 1:
            if other == 0 or other == '0':
                return True
        elif self.value == 'U':
            if other == 'U' or other == 'u':
                return True
        return False

    def __and__(self, other):
        if self == 1:
            if other == 1:
                return Value('1')
            if other == 'U':
                return Value('U')
        return Value('0')

    def __or__(self, other):
        if self == 1 or other == 1:
            return Value(1)
        if self == 'U' or other == 'U':
            return Value('U')
        return Value(0)

    def __invert__(self):
        if self == 1:
            return Value(0)
        if self == 0:
            return Value(1)
        return Value('U')

    def __str__(self):
        return str(self.value)


class Node(object):
    def __init__(self, gate: Gate):
        self.name = gate.name
        self.gate_type = gate.type
        self.update = gate.update
        self.logic = gate.logic
        self.input_names = gate.input_names
        self.value_new = gate.value_new
        self.value = gate.value
        self.type = 'wire'
        self.input_nodes = []
        self.output_nodes = []

    def __eq__(self, other):
        if self.value == other:
            return True
        return False

    def __str__(self):
        return f"{str(self.type):6}\t{str(self.name):5} = {self.value:^4}"

    def reset(self):
        self.value = Value('U')
        self.value_new = Value('U')

    def set(self, value:Value):
        self.value = value
        self.value_new = value

class Gate(object):
    def __init__(self, name: str, inputs: []):
        self.input_names = inputs
        self.input_nodes = []
        self.output_nodes = []
        self.name = name
        self.value = Value('U')
        self.value_new = Value('U')
        self.type = "wire"

    def update(self):
        self.value = self.value_new

    def logic(self):
        # Do not change
        pass

class And(object, Gate):
    def __init__(self, name, inputs:[]):
        super(And, self).__init__(name, inputs)
        self.type = "AND"

    def logic(self):
        if any(node == 0 for node in self.input_nodes):
            self.value_new = Value(0)
        elif all(node == 1 for node in self.input_nodes):
            self.value_new = Value(1)
        else:
            self.value_new = Value('U')


class Or(object, Gate):
    def __init__(self, name, inputs:[]):
        super(Or, self).__init__(name, inputs)
        self.type = "OR"

    def logic(self):
        if any(node == 1 for node in self.input_nodes):
            self.value_new = Value(1)
        elif any(node == 'U' for node in self.input_nodes):
            self.value_new = Value('U')
        else:
            self.value_new = Value(0)


class Nand(object, Gate):
    def __init__(self, name, inputs:[]):
        super(Nand, self).__init__(name, inputs)
        self.type = "NAND"

    def logic(self):
        if any(node == 0 for node in self.input_nodes):
            self.value_new = Value(1)
        elif any(node == 'U' for node in self.input_nodes):
            self.value_new = Value('U')
        self.value_new = Value(0)


class Not(object, Gate):
   def __init__(self, name, inputs:[]):
       super(Not, self).__init__(name, inputs)
       self.type = "NOT"

    def logic(self):
        self.value_new = ~self.input_nodes[0].value


class Xnor(object, Gate):
    def __init__(self, name, inputs:[]):
        super(Xnor, self).__init__(name, inputs)
        self.type = "XNOR"

    def logic(self):
        pass
        # TDDO: logic


class Xor(object, Gate):
    def __init__(self, name, inputs:[]):
        super(Xor, self).__init__(name, inputs)
        self.type = "XOR"

    def logic(self):
        pass
        # TODO: logic

class Nor(object, Gate):
    def __init__(self, name, inputs:[]):
        super(Nor, self).__init__(name, inputs)
        self.type = "NOR"

    def logic(self):
        if any(node == 1 for node in self.input_nodes):
            self.value_new = Value(0)
        if any(node == 'U' for node in self.input_nodes):
            self.value_new = Value('U')
        self.value_new = Value(1)


class Buff(object, Gate):
    def __init__(self, name, inputs:[]):
        super(Buff, self).__init__(name, inputs)
        self.type = "BUFF"

    def logic(self):
        self.value_new = self.input_nodes[0].value
