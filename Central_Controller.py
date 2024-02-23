from enum import Enum
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from Execution_Policy import ExecutionPolicy, OnlineExecutionPolicy
from Unit_Execution_Policy import UnitExecutionPolicy
from Fully_Synchronised_Policy import FSP, OnlineFSP  # noqa: F401
from Minimum_Communication_Policy import MCP, OnlineMCP  # noqa: F401
from Position import Position


class GetRequest(Enum):
    GET_NEXT_POSITION = "/"
    GET_LOCATIONS = "/get_locations"
    GET_STATUS = "/get_status"

class PostRequest(Enum):
    POST_ROBOT_STATUS = "/"
    POST_EXTEND_PATH = "/extend_path"

class CentralController(BaseHTTPRequestHandler):
    """
    A class representing the central controller for a multi-agent system.

    Attributes:
    - execution_policy (ExecutionPolicy): An execution policy object
    that determines the next position of an agent.
    """
    request_version = "HTTP/1.1"

    execution_policy: ExecutionPolicy | OnlineExecutionPolicy = UnitExecutionPolicy(1)

    def do_GET(self):
        """
        Handles GET requests from agents.

        Returns:
        - None
        """
        self.request_version
        url = urlparse(self.path)

        match GetRequest(url.path):
            case GetRequest.GET_NEXT_POSITION:  # Should do a pattern match
                query = urlparse(self.path).query
                content_length = int(self.headers.get("Content-Length", 0))
                agent_id = parse_qs(query).get("agent_id", None)
                if content_length > 0:
                    raw_data = self.rfile.read(content_length)
                    data = json.loads(raw_data)

                if not agent_id:
                    agent_id = str(data.get('agent_id', None))
                    if agent_id is None:
                        print("No agent id provided, cannot give next position")
                        return

                if not agent_id[0].isdigit():
                    print("Agent id provided is malformed, cannot convert to int")
                    return

                agent_id = int(agent_id[0])

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                message = {}
                message["agent_id"] = agent_id

                # Fullfill agents request for position data
                (
                    positions,
                    (start_timestep, end_timestep),
                ) = CentralController.execution_policy.get_next_position(agent_id)
                message["start_timestep"], message["end_timestep"] = (
                    start_timestep,
                    end_timestep,
                )

                if isinstance(positions, list):
                    message["positions"] = [pos.to_tuple() for pos in positions]
                elif isinstance(positions, Position):
                    print(
                        "Warning: This is deprecated, moved to List[Position] for get_next_position()"
                    )
                    message["position"] = positions.to_tuple()
                else:
                    raise TypeError(f"Position {positions} as type {type(positions)}")

                self.wfile.write(bytes(json.dumps(message), "utf-8"))
            case GetRequest.GET_LOCATIONS:
                if not isinstance(self.execution_policy, OnlineExecutionPolicy):
                    assert(False), "Unsupported request for the ExeuctionPolicy"
                (
                    locations,
                    all_ready,
                ) = CentralController.execution_policy.get_agent_locations()
                if not all_ready:
                    self.send_response(404)
                    self.end_headers()
                    return


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

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", f"{len(json.dumps(message))}")
                self.end_headers()

                self.wfile.write(bytes(json.dumps(message), "utf-8"))
            case GetRequest.GET_STATUS:
                if not isinstance(self.execution_policy, OnlineExecutionPolicy):
                    assert(False), "Unsupported API request for ExecutionPolicy"
                (
                    locations,
                    all_ready,
                ) = CentralController.execution_policy.get_agent_locations()
                if not all_ready:
                    self.send_response(404)
                    self.end_headers()
                    return
                statuses = CentralController.execution_policy.get_status()

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
                message["status"] = [
                    {
                        "status": str(status),
                        "agent_id": agent_id,
                    }
                    for (agent_id, status) in statuses]
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", f"{len(json.dumps(message))}")
                self.end_headers()

                self.wfile.write(bytes(json.dumps(message), "utf-8"))
            case _:
                print(f"Unexpected path {url.path}")

    def do_POST(self):
        """
        Handles POST requests from agents.

        Returns:
        - None
        """
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        match PostRequest(urlparse(self.path).path):
            case PostRequest.POST_ROBOT_STATUS:
                CentralController.execution_policy.update(data)
            case PostRequest.POST_EXTEND_PATH:
                if not isinstance(self.execution_policy, OnlineExecutionPolicy):
                    assert(False), "Unsupported request for the ExeuctionPolicy"

                extensions = []
                for state in data["plans"]:  # The index is the agent_id
                    extensions.append(
                        (
                            state["agent_id"],
                            [
                                Position(
                                    int(0.5 + state["x"]),
                                    int(0.5 + state["y"]),
                                    int(0.5 + state["theta"]),
                                ),
                            ],
                        )
                    )
                CentralController.execution_policy.extend_plans(extensions)
            case _:
                print("Unexpected path {self.path}")
        # Update execution policy with incoming agent data.
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", f"{len(post_data)}")
        self.end_headers()
        self.wfile.write(post_data)
