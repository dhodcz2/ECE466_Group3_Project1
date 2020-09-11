class ParseLineError(object, Exception):
    def __init__(self, line):
        self.line = line
        super(ParseLineError, self).__init__()

    def __str__(self):
        return f"Line unable to be parsed: {self.line}"

class ParseInputNumberError(object, Exception):
    def __init__(self, line):
        self.line = line
        super(ParseInputsError, self).__init__()

    def __str__(self):
        return f"Invalid number of inputs: {self.line}"

class ParseNoGateError(object, Exception):
    def __init__(self, name):
        self.name = name
        super(NoInputError, self).__init__()

    def __str__(self):
        return f"Output created, but no corresponding logic gate: {self.name}"

class ParseInputNotFoundError(object, Exception):
    def __init__(self, line, name):
        self.line = line
        self.name = name
        super(InputNotFoundError, self).__init__()

    def __str__(self):
        return f"Cannot find corresponding node {self.name} from {self.line}"

