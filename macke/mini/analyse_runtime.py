"""
Generate a json file with all runtime information inside a Macke run directory
"""

from collections import OrderedDict
import json
from os import path


def analyse_runtime(macke_directory):
    """
    Collect and summarize the runtime information of all KLEE runs
    """

    # Read klee.json information
    klees = dict()
    with open(path.join(macke_directory, 'klee.json')) as klee_json:
        klees = json.load(klee_json)

    result = OrderedDict()
    result['total'] = 0
    result['phase'] = {'1': 0, '2': 0}
    result['entrypoint'] = {}

    for _, klee in klees.items():
        # Load runtime information from run.stats
        runtime = 0
        with open(path.join(klee['folder'], 'run.stats')) as run_stats:
            # Read the entire file
            stats = run_stats.readlines()

            # Read the position of UserTime
            runtimepos = stats[0][1:-1].split(",").index("'UserTime'")

            # Read the last row - it contains the overall values
            runtime = float(stats[-1][1:-1].split(",")[runtimepos])

        result['total'] += runtime
        result['phase'][str(klee['phase'])] += runtime

        if klee['phase'] == 1:
            entry = result['entrypoint'].get(
                klee['function'], {'1': 0, '2': 0})
            entry['1'] += runtime
            result['entrypoint'][klee['function']] = entry
        elif klee['phase'] == 2:
            entry = result['entrypoint'].get(
                klee['caller'], {'1': 0, '2': 0})
            entry['2'] += runtime
            result['entrypoint'][klee['caller']] = entry

    runtime_json = path.join(macke_directory, "runtime.json")

    with open(runtime_json, 'w') as f:
        json.dump(result, f)

    print("The runtime analysis was stored in", runtime_json)


def main():
    """
    Parse command line arguments and start analyse_runtime function
    """

    import argparse
    parser = argparse.ArgumentParser(
        description="""\
        Add a summary of all KLEE runtimes to the directory of a MACKE run
        """
    )
    parser.add_argument(
        "mackedir",
        help="The directory of a MACKE run to be analyzed")

    args = parser.parse_args()

    if (path.isdir(args.mackedir) and
            path.isfile(path.join(args.mackedir, 'klee.json'))):
        analyse_runtime(args.mackedir)
    else:
        print("ERROR: '%s' is not a directory of a MACKE run" % args.mackedir)

if __name__ == '__main__':
    main()
