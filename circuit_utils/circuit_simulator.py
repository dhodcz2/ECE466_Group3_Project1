from _collections import OrderedDict
from circuit_utils import nodes
from circuit_utils import exceptions
from re import match


class CircuitSimulator(object):
    class IterationPrinter(object):
        def generate_line(self, node:nodes.Node):
            line1 = node.type
            line2 = node.name
            line3 = node.gate_type.ljust(8) if node.gate_type else ""
            line3 += ', '.join(node.input_names)
            line4 = str(node.value)
            line = line1.ljust(11) + line2.ljust(8) + line3.ljust(20) + line4.ljust(3)
            return line

        def __init__(self, nodes):
            self.iteration = 0
            self.lines = [self.generate_line(node) for node in nodes]
            header = "Type".ljust(8) + "Variable".ljust(11) + "Logic".ljust(8) + "Inputs".ljust(9) + "Initial".ljust(3)
            self.lines.insert(0, header)

        def __iter__(self):
            for line in self.lines:
                yield line

        def __str__(self):
            string = ""
            for line in self:
                string += line + "\n"
            return string

        def __call__(self, nodes):
            # assert(len(nodes) == len(self.lines))
            self.iteration += 1
            self.lines[0] += "\t" + str(self.iteration)
            i = 0
            for node in nodes:
                self.lines[i + 1] += "\t" + str(node.value)
                i += 1

    class LineParser(object):
        def __init__(self, bench):
            self.file = bench
            self.pattern_gate = "(\S+) = ([A-Z]+)\((.+)\)"
            self.pattern_io = "([A-Z]+)\((.+)\)"
            self.gates = []
            self.input_names = []
            self.output_names = []
            self.gate_map = {"AND": nodes.AndGate, "OR": nodes.OrGate, "NAND": nodes.NandGate, "XNOR": nodes.XnorGate,
                             "NOR": nodes.NorGate, "BUFF": nodes.BuffGate, "XOR": nodes.XorGate, "NOT": nodes.NotGate}

        def parse_file(self):
            with open(self.file) as f:
                for line in f:
                    self.parse_line(line)
            return self

        def parse_line(self, line: str):
            if groups := match(self.pattern_gate, line):
                name = groups.group(1)
                gate_type = self.gate_map[groups.group(2)]
                if not gate_type:
                    raise exceptions.ParseLineError(line)
                inputs = groups.group(3).split(', ')
                self.gates.append(gate_type(name, inputs))
            elif groups := match(self.pattern_io, line):
                io = groups.group(1)
                name = groups.group(2)
                if io == "INPUT":
                    self.input_names.append(name)
                    self.gates.append(nodes.Gate(name))
                elif io == "OUTPUT":
                    self.output_names.append(name)
                else:
                    raise exceptions.ParseLineError(line)
            elif line.startswith('#') or line == '\n':
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
            elif item in self.input_nodes:
                return self.input_nodes[item]
            elif item in self.output_nodes:
                return self.output_nodes[item]
            return KeyError

        def __iter__(self):
            for node in self.input_nodes.values():
                yield node
            for node in self.intermediate_nodes.values():
                yield node
            for node in self.output_nodes.values():
                yield node

        def __str__(self):
            string = ''
            for node in self:
                string += f"\n{node}"
            return string

    def __init__(self, args):
        self.nodes = self.Nodes()
        self.args = args
        self.parser = self.LineParser(args.bench)
        self.compile(self.parser.parse_file())

    def __next__(self):
        if self.iteration == 0:
            self.iteration += 1
            return "Inital values:" + str(self.nodes)
        self.iteration += 1
        updated_nodes = 0
        for node in self.nodes:
            node.logic()
            if node.value != node.value_new:
                updated_nodes += 1
        if updated_nodes == 0:
            raise StopIteration
        for node in self.nodes:
            node.update()
        return "Iteration # " + str(self.iteration) + ": " + str(self.nodes)

    def __iter__(self):
        self.iteration = 0
        return self

    def __str__(self):
        string = ''
        for node in self.nodes:
            string += f"{node}\n"

    def compile(self, lineparser: LineParser):
        # Compile a list of nodes from the parsed gates
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
        # Update Node member vectors input_nodes and output_nodes, which hold references to connected nodes
        for node in self.nodes:
            for input_name in node.input_names:
                self.nodes[node.name].input_nodes.append(self.nodes[input_name])
                self.nodes[input_name].output_nodes.append(self.nodes[node.name])

    def prompt(self):
        #for node in self.nodes.input_nodes:
            #print(node)
        #print()
        line = self.args.testvec
        if not line:
            line = input("Start simulation with input values (return to exit):")
            if not line:
                return False
        for character, node in zip(line, self.nodes.input_nodes.values()):
            node.set(nodes.Value(character))
        return True

    def simulate(self):
        if self.args.verbose:
            print('Simulating with the following input values:')
            #for node in self.nodes.input_nodes.values():
                #print(node)
            #print()

        iteration_printer = self.IterationPrinter(self.nodes)
        #print(iteration_printer)
        for iteration in self:
            iteration_printer(self.nodes)

        print(iteration_printer)

        # if self.args.verbose
        # for iteration in self:
            # if self.args.verbose:
                # print(iteration, "\n")

    def create_fault(self):
        #     TODO: Prompt the user for for faulty node, and SA-0 or SA-1
        pass

    def detect_fault(self):
        #     TODO: Detect any faults that have propagated to the outputs
        pass

    def reset(self):
        for node in self.nodes:
            node.reset()
