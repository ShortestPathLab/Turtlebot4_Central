from typing import List, Tuple
import os, logging

def load_paths(path_file: str = None) -> List[List[Tuple[int]]]:

    print("Loading paths from "+str(path_file), end="... ")
    if not os.path.exists(path_file):
        logging.warning("\nNo path file is found!")
        return

    paths = dict()
    with open(path_file, mode="r", encoding="utf-8") as fin:
        # ag_counter = 0
        for line in fin.readlines():
            if line.split(" ")[0] != "Agent":
                break
            ag_idx = int(line.split(" ")[1].split(":")[0])
            paths[ag_idx] = list()
            for cur_loc in line.split(" ")[-1].split("->"):
                if cur_loc == "\n":
                    continue
                cur_x = int(cur_loc.split(",")[1].split(")")[0])
                cur_y = int(cur_loc.split(",")[0].split("(")[1])
                paths[ag_idx].append((cur_x, cur_y))
            # ag_counter += 1

        # num_of_agents = ag_counter

    # for ag_idx in range(self.num_of_agents):
    #     if self.makespan < max(len(paths[ag_idx])-1, 0):
    #         self.makespan = max(len(paths[ag_idx])-1, 0)

    print("Done!")
    return paths