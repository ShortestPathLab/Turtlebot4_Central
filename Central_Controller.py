import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from Execution_Policy import ExecutionPolicy, OnlineExecutionPolicy
from Fully_Synchronised_Policy import FSP, OnlineFSP # noqa: F401
from Minimum_Communication_Policy import MCP, OnlineMCP # noqa: F401
from Position import Position


class CentralController(BaseHTTPRequestHandler):
    """
    A class representing the central controller for a multi-agent system.

    Attributes:
    - execution_policy (ExecutionPolicy): An execution policy object
    that determines the next position of an agent.
    """

    execution_policy: ExecutionPolicy | OnlineExecutionPolicy = OnlineMCP(1)

    def do_GET(self):
        """
        Handles GET requests from agents.

        Returns:
        - None
        """

        url = urlparse(self.path)
        match url.path:
            case "/":  # Should do a pattern match
                query = urlparse(self.path).query
                agent_id = parse_qs(query).get("agent_id", None)

                if not agent_id:
                    return

                if not agent_id[0].isdigit():
                    return

                agent_id = int(agent_id[0])

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                message = {}
                message["agent_id"] = agent_id

                # Fullfill agents request for position data
                (
                    position,
                    timestep,
                ) = CentralController.execution_policy.get_next_position(agent_id)

                message["timestep"] = timestep
                message["position"] = position.to_tuple()
                self.wfile.write(bytes(json.dumps(message), "utf-8"))
            case "/get_locations":
                locations = CentralController.execution_policy.get_agent_locations()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                message = {}

                # Ideally this is in row-column format with only positive values for the planner
                # Right now the planner side converts row-column to pos-x, neg-y
                message["locations"] = [
                    {
                        "x": location.x,
                        "y": location.y,
                        "theta": location.theta,
                        "agent_id": agent_id,
                    }
                    for (location, agent_id) in locations
                ]

                self.wfile.write(bytes(json.dumps(message), "utf-8"))

            case _:
                print(f"Did not expect {url.path}")

    def do_POST(self):
        """
        Handles POST requests from agents.

        Returns:
        - None
        """
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        match urlparse(self.path).path:
            case "/":
                CentralController.execution_policy.update(data)
            case "/extend_path":
                extensions = []
                for agent_id, state in enumerate(
                    data["plans"]
                ):  # The index is the agent_id
                    extensions.append(
                        (
                            agent_id,
                            [
                                (
                                    Position(state["x"], state["y"], state["theta"]),
                                    state["timestep"],
                                )
                            ],
                        )
                    )
                CentralController.execution_policy.extend_plans(extensions)
            case _:
                print("Unexpected path {self.path}")
        # Update execution policy with incoming agent data.
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(post_data)


class OnlineCentralController(CentralController):
    pass
