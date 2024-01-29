import requests
import json
from typing import Any


def main(path_to_path_file: str, hostname: str, port: str):
    """File formatted as
    \"{agent_id}: [Position(0,0,90), Position(0,-1,90)]\"
    Meaning the robot with agent_id is at (0,0) at t=0, then moves to (0,-1) at t=1
    """

    with open(path_to_path_file) as f:
        for line in f.readlines():
            if not line.strip(): # Stop at blank line
                break
            _agent_id, path = line.split(": ")
            agent_id = int(_agent_id)
            message: Any = {}
            message["plans"] = []
            #  [(4.0,0.0,90.0), (4.0,-0.0,0.0), (4.0,-0.0,90.0)] parse for tuples in list
            for timestep, triple in enumerate(path[1:-2].split(", ")):
                print(triple)
                x, y, theta = map(float, triple[1:-2].split(","))
                message["plans"].append(
                        {
                            "x": x,
                            "y": y,
                            "theta": theta,
                            "agent_id": agent_id,
                            "timestep": timestep,
                        }
                )
            requests.post(f"http://{hostname}:{port}/extend_path", json.dumps(message))

if __name__ == "__main__":
    main("path.txt", "127.0.0.1", "8080")
