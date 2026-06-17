from cachetools import TTLCache
from fastmcp import FastMCP, Client


# necessary in case of empty client config
empty_server = FastMCP("EmptyServer")


class MCPClient(Client):
    """Cat MCP client is scoped by user_id and does not keep a live connection to servers.
        We use caches waiting for the protocol to become stateless.
    """

    def __init__(self, config):

        # TODO: get addresses / tokens / api keys from DB
        self.config = config
        if len(config["mcpServers"]) == 0:
            super().__init__(empty_server)
        else:
            super().__init__(config)


class MCPClients():
    """Keep a cache of user scoped MCP clients"""

    def __init__(self):
        self.clients = TTLCache(maxsize=1000, ttl=60*10)
    
    def get_user_client(self, agent) -> MCPClient:
        
        need_new, config = self.need_new_client(agent)
        if need_new:
            self.clients[agent.user.id] = MCPClient(config)

        return self.clients[agent.user.id]
    
    def need_new_client(self, agent) -> tuple[bool, dict]:
        
        config = {
            "mcpServers": {}
        }

        for slug, server_config in {}: # TODOV2 RECOVER
            config["mcpServers"][slug] = {
                "url": str(server_config.url)
            }
        for server_config in []: # TODOV2 RECOVER
            config["mcpServers"][server_config.name] = {
                "url": str(server_config.url)
            }
        
        need_new = (agent.user.id not in self.clients) \
            or self.clients[agent.user.id].config != config

        return (
            need_new,
            config
        )
        

    
        

    
