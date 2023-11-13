import json
from http.server import BaseHTTPRequestHandler
from typing import Dict, List
from urllib.parse import parse_qs, urlparse

from Execution_Policy import ExecutionPolicy

# from Fully_Synchronised_Policy import FSP
from Minimum_Communication_Policy import MCP


class CentralController(BaseHTTPRequestHandler):
    """
    A class representing the central controller for a multi-agent system.

    Attributes:
    - execution_policy (ExecutionPolicy): An execution policy object
    that determines the next position of an agent.
    """

    execution_policy: ExecutionPolicy = MCP("result.path", 2)

    def do_GET(self):
        """
        Handles GET requests from agents.

        Returns:
        - None
        """
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
        position, timestep = CentralController.execution_policy.get_next_position(
            agent_id
        )

        message["timestep"] = timestep
        message["position"] = position.to_tuple()
        self.wfile.write(bytes(json.dumps(message), "utf-8"))

    def do_POST(self):
        """
        Handles POST requests from agents.

        Returns:
        - None
        """
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        # Update execution policy with incoming agent data.
        CentralController.execution_policy.update(data)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(post_data)
