from circuit_utils import circuit_simulator
import argparse
import logging

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bench', type=str, default='circuit.bench', help='input bench file')
    parser.add_argument('-v', '--verbose', type=bool, default=True, help='verbose simulator')
    args = parser.parse_args()

    simulator = circuit_simulator.CircuitSimulator(args)
    while(simulator.prompt()):
        simulator.simulate()
    print("Finished -- bye!")
