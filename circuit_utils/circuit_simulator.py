from _collections import OrderedDict
from circuit_utils import nodes
from circuit_utils import exceptions
from re import match


class CircuitSimulator(object):
    class LineParser(object):
        def __init__(self):
            self.file = CircuitSimulator.args.bench
            self.pattern_gate = "(\S+) = ([A-Z]+)\((.+)\)"
            self.pattern_io = "([A-Z]+)\((.+)\)"
            self.gates = []
            self.input_names = []
            self.output_names = []
            self.gate_map = {"AND": nodes.And, "OR": nodes.Or, "NAND": nodes.Nand, "XNOR": nodes.Xnor,
                             "NOR": nodes.Nor, "BUFF": nodes.Buff, "XOR": nodes.Xor, "NOT": nodes.Not}

        def parse_file(self):
            with open(self.file) as f:
                for line in f:
                    self.parse_Line(f)
            return self

        def parse_line(self, line: str):
            if groups := match(self.pattern_gate, line):
                name = groups[0]
                gate_type = self.gate_map[groups[1]]
                if not gate_type:
                    raise exceptions.ParseLineError(line)
                inputs = groups[2].split(', ')
                self.gates.append(gate_type(name, inputs))
            elif groups := match(self.pattern_io, line):
                name = groups[0]
                if match[0] == "INPUT":
                    self.input_names.append(name)
                    self.gates.append(nodes.Gate(name))
                elif match[0] == "OUTPUT":
                    self.output_names.append(name)
                else:
                    raise exceptions.ParseLineError(line)
            elif line.startswith('#') or line == '':
                pass
            else:
                raise exceptions.ParseLineError(line)

    class Nodes(object):
        def __init__(self):
            self.input_nodes = OrderedDict()
            self.intermediate_nodes = OrderedDict()
            self.output_nodes = OrderedDict()

        def __contains__(self, item: nodes.Node):
            if item in self.intermediate_nodes:
                return True
            if item in self.input_nodes:
                return True
            if item in self.output_nodes:
                return True
            return False

        def __getitem__(self, item: nodes.Node):
            if item in self.intermediate_nodes:
                return self.intermediate_nodes[item]
            if item in self.input_nodes:
                return self.input_nodes[item]
            if item in self.output_nodes:
                return self.output_nodes[item]
            return KeyError

        def __iter__(self):
            for node in self.input_nodes:
                yield node
            for node in self.intermediate_nodes:
                yield node
            for node in self.output_nodes:
                yield node

        def __str__(self):
            string = ''
            for node in self:
                string += f"\n{node}"
            return string

    def __init__(self, args):
        self.nodes = self.Nodes()
        self.args = args
        self.parser = self.LineParser()
        self.compile(self.parser.parse())

    def __iter__(self):
        self.stop_iterating = False
        return self

    def __next__(self):
        updated_nodes = 0
        if self.stop_iterating:
            for node in self.nodes:
                node.reset()
            raise StopIteration
        for node in nodes:
            node.logic()
            if node.value != node.value_new:
                updated_nodes += 1
            if updated_nodes == 0:
                self.stop_iterating = True
        for node in nodes:
            node.update()
        return str(nodes)

    def __str__(self):
        string = ''
        for node in self:
            string += f"{node}\n"

    def compile(self, lineparser: LineParser):
        for gate in lineparser.gates:
            node = nodes.Node(gate)
            if node.name in lineparser.input_names:
                node.type = 'input'
                self.nodes.input_nodes.update({node.name: node})
            elif node.name in lineparser.output_names:
                node.type = 'output'
                self.nodes.output_nodes.update({node.name: node})
            else:
                self.nodes.intermediate_nodes.update({node.name: node})
        for node in self.nodes:
            for input_name in node.input_names:
                self.nodes[node.name].input_nodes.append(self.nodes[input_name])
                self.nodes[input_name].outpud_nodes.apppend(self.nodes[node.name])

    def prompt(self):
        for node in self:
            print(node)
        print("---------------")
        line = input("Start simulation with input values (return to exit):")
        if not line:
            return False
        for character, node in zip(line, self.nodes.input_nodes):
            node.set(nodes.Value(character))
        return True

    def simulate(self):
        if self.args.verbose:
            print('Simulating with the following input values')
            for node in self.nodes.input_nodes:
                print(node)
        for iteration in self:
            if self.args.verbose:
                print(iteration)

    def reset(self):
        for node in self.nodes:
            node.reset()
