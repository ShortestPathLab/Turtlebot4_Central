import os
from typing import Dict, List

from Position import Position


def load_paths(path_file: str | None = None) -> Dict[int, List[Position]]:
    """
    Load paths from a file and return a dictionary of paths for each agent.

    Args:
        path_file (str): The path to the file containing the paths.

    Returns:
        A dictionary of paths for each agent, where the key is the
        agent index and the value is a list of Positions.
    """

    print("Loading paths from " + str(path_file), end="... ")
    if path_file is None or not os.path.exists(path_file):
        print("\nNo path file is found!")
        exit(1)

    paths: Dict[int, List[Position]] = dict()
    with open(path_file, mode="r", encoding="utf-8") as fin:
        for line in fin.readlines():
            if line.split(" ")[0] != "Agent":
                break
            ag_idx = int(line.split(" ")[1].split(":")[0])
            paths[ag_idx] = list()
            for cur_loc in line.split(" ")[-1].split("->"):
                if cur_loc == "\n":
                    continue
                cur_x = float(cur_loc.split(",")[1])
                cur_y = float(cur_loc.split(",")[0].split("(")[1])
                cur_theta = float(cur_loc.split(",")[2].split(")")[0])
                paths[ag_idx].append(Position(cur_x, cur_y, cur_theta))
    return paths
