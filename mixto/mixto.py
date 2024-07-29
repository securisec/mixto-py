import json
from pathlib import Path
from urllib.parse import urljoin
from typing import Optional, Dict, Any, Union
from .lib.gql import GraphqlClient
from .types import MixtoConfig
from requests import Session


class Mixto:
    def __init__(
        self, host: str = "", api_key: str = "", config_file=Path.home() / ".mixto.json"
    ):
        self.host = host
        self.api_key = api_key
        self.config_file = config_file
        self.config: Union[MixtoConfig, Any] = {}

        if not any([self.host, self.api_key]):
            self.config = MixtoConfig(**json.loads(self.config_file.read_text()))
            self.host, self.api_key = self.config.host, self.config.api_key
            if not any([self.host, self.api_key]):
                raise ValueError("Host and api key not specified")

        self.gql_client = GraphqlClient(
            endpoint=host, headers={"x-api-key": self.api_key}
        )
        self.rest_client = Session()
        self.rest_client.headers = {"x-api-key": self.api_key}

    def _make_url(self, path: str) -> str:
        return urljoin(self.host, path)

    def graphql(self, query: str, variables: Dict[str, Any] = {}) -> Dict:
        """Make a user graphql query

        Args:
            query (str): Query
            variables (Dict[str, Any], optional): Option variables. Defaults to {}.

        Raises:
            ValueError: If status code is not 200

        Returns:
            Dict: Graphql response
        """
        self.gql_client.endpoint = self.host + "/api/v1/gql"
        r, status = self.gql_client.execute(query=query, variables=variables)
        if status != 200:
            raise ValueError(r)
        return r["data"]

    def graphql_admin(self, query: str, variables: Dict[str, Any] = {}) -> Dict:
        """Make an admin graphql query

        Args:
            query (str): Query
            variables (Dict[str, Any], optional): Option variables. Defaults to {}.

        Raises:
            ValueError: If status code is not 200

        Returns:
            Dict: Graphql response
        """
        self.gql_client.endpoint = self.host + "/api/admin/gql"
        r, status = self.gql_client.execute(query=query, variables=variables)
        if status != 200:
            raise ValueError(r)
        return r["data"]

    def graphql_subscribe(self, query: str, variables: Optional[Dict[str, Any]] = None):
        # TODO 🔥
        raise NotImplementedError

    def graphql_admin_subscribe(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ):
        # TODO 🔥
        raise NotImplementedError

    def user_get(self):
        return self.rest_client.get(self._make_url("/api/v1/user")).json()

    def user_update(self, username: str, avatar: str):
        return self.rest_client.post(
            self._make_url("/api/v1/user"),
            json={"username": username, "avatar": avatar},
        ).json()

    def user_reset_api_key(self):
        return self.rest_client.delete(self._make_url("/api/v1/user"))

    def workspace_get_entries(
        self, workspace_id: str = "", include_commits: bool = False
    ):
        if workspace_id == "":
            workspace_id = self.config.workspace_id
        return self.rest_client.post(
            self._make_url("/api/v1/workspace"),
            json={"workspace_id": workspace_id, "include_commits": include_commits},
        ).json()

    def workspace_get_all(self):
        return self.rest_client.get(self._make_url("/api/v1/workspace")).json()

    def entry_get_commits(self, entry_id: str):
        return self.rest_client.post(
            self._make_url("/api/v1/workspace/commits"), json={"entry_id": entry_id}
        ).json()

    def admin_workspace_export(self):
        # TODO 🔥
        pass

    def admin_workspace_import(self):
        # TODO 🔥
        pass

    def admin_reindex_workspace(self):
        # TODO 🔥
        pass

    def admin_reindex_all_workspaces(self):
        # TODO 🔥
        pass

    def admin_get_workspace_backups(self):
        # TODO 🔥
        pass

    def admin_backup_workspace(self):
        # TODO 🔥
        pass

    def admin_restore_workspace(self):
        # TODO 🔥
        pass

    def commit_add(self):
        # TODO 🔥
        pass

    def file_upload(self):
        # TODO 🔥
        pass

    def file_get(self):
        # TODO 🔥
        pass

    def admin_file_get_all(self):
        # TODO 🔥
        pass

    def admin_file_delete(self):
        # TODO 🔥
        pass
