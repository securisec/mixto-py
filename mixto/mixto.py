import sys

from mixto.types.entry import (
    Activity,
    Commit,
    CommitTag,
    Description,
    Entry,
    Flag,
    Like,
    Note,
)
from mixto.types.misc import (
    CommitTypes,
    Etag,
    Hit,
    ValidDataTypes,
    Workspace,
    Version,
)
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urljoin, urlencode
from pathlib import Path
from json import dumps, loads
from subprocess import getoutput
from typing import Any, Dict, List, Optional, Union
from .exceptions import BadResponse
from .types.user import AvatarImage, Settings, User, UserStats
from .types.admin import AdminFile, Backup, ServiceAccount
from pydantic import parse_obj_as

from .__version__ import __version__


class Mixto:
    def __init__(
        self, host: str = None, api_key: str = None, workspace: str = None
    ) -> None:
        super().__init__()
        self.host: Optional[str] = host
        self.api_key: Optional[str] = api_key
        self.workspace: Union[str, None] = workspace
        self.status: int = 0
        self.commit_type: CommitTypes = "script"

        if self.host == None or self.api_key == None:
            try:
                conf_path = str(Path().home() / ".mixto.json")
                with open(conf_path) as f:
                    j = loads(f.read())
                    self.host = j["host"]
                    self.api_key = j["api_key"]
                    # if user did not specify workspace, use the one in the config
                    self.workspace = (
                        self.workspace if self.workspace else j["workspace"]
                    )
            except:
                print("Cannot read Mixto config")

    @property
    def _workspace(self):
        if self.workspace == None:
            raise Exception("No workspace set")
        return self.workspace

    def _make_request(
        self,
        method: str,
        uri: str,
        body: Any = {},
        isJson: bool = True,
        queryParams: dict = {},
    ) -> Any:
        url = urljoin(str(self.host), uri)
        q = ""
        if queryParams:
            q = "?" + urlencode(queryParams)
        req = Request(
            method=method.upper(),
            url=url + q,
            data=dumps(body).encode(),
            headers={
                "x-api-key": str(self.api_key),
                "user-agent": "mixto-py-{}".format(__version__),
            },
        )
        if body:
            req.add_header("Content-Type", "application/json")
        try:
            res = urlopen(req)
            body = res.read()
            self.status = res.getcode()
            if self.status > 300:
                raise BadResponse(self.status, res)
            if isJson:
                return loads(str(body.decode()))
            else:
                return body
        except HTTPError as e:
            raise BadResponse(e.code, e.read())

    def api_version(self) -> Version:
        """Get app version information

        Returns:
            Version: App version information
        """
        r = self._make_request("get", "/api/misc")
        return Version(**r)

    def get_tags(self) -> List[str]:
        """Get a list of all tags in the instance

        Returns:
            List[str]: List of tags
        """
        r = self._make_request("get", "/api/misc/tags")
        return r

    def get_etag(self) -> Etag:
        """Get the current etag and time created

        Returns:
            Etag: Etag
        """
        r = self._make_request("get", "/api/misc/time")
        return Etag(**r)

    def valid_data_types(self) -> ValidDataTypes:
        """Get a list of valid categories

        Returns:
            ValidateDataTypes: List of valid data types
        """
        r = self._make_request("get", "/api/misc/categories")
        return ValidDataTypes(**r)

    def get_workspace(self) -> List[Entry]:
        """Get a list of redacted entries for a workspace

        Returns:
            List[Entry]: List of entries for a workspace
        """
        r = self._make_request("get", f"/api/misc/workspaces/{self._workspace}")
        return parse_obj_as(List[Entry], r)

    def user_info(self) -> User:
        """Get user info

        Returns:
            UserInfo: User info
        """
        return User(**self._make_request("get", "/api/user"))

    def user_update(self, username: str, avatar: str) -> None:
        """Update username and avatar avatar. The avatar should be a
        valid URL to an image.

        Args:
            username (str): Username
            avatar (str): Avatar url
        """
        self._make_request(
            "post",
            "/api/user",
            body={
                "username": username,
                "avatar": avatar,
            },
            isJson=False,
        )
        return None

    def get_avatar_image(self) -> AvatarImage:
        """Generate a new avatar image

        Returns:
            AvatarImage: Avatar image
        """
        return AvatarImage(**self._make_request("get", "/api/user/avatar"))

    def user_reset_apikey(self) -> Dict[str, str]:
        """Reset user api key

        Returns:
            Dict[str ,str]: Contains ``new_api_key`` and ``old_api_key``
        """
        return self._make_request("get", "/api/user/reset")

    def user_get_settings(self) -> Settings:
        """Get a dict of current user settings

        Returns:
            Settings: User settings dict
        """
        r = self._make_request("get", "/api/user/settings")
        return parse_obj_as(Settings, r)

    def user_update_settings(self, **body) -> Settings:
        """Set a users settings

        Args:
            dark_theme (bool): Enable or disable dark theme

        Returns:
            Settings: New settings
        """
        r = self._make_request("post", "/api/user/settings", body)
        return Settings(**r)

    def get_user_stats_for_workspace(self) -> List[UserStats]:
        """Get a list of user stats for a workspace

        Returns:
            List[UserStats]: List of user stats
        """
        r = self._make_request(
            "post", f"/api/user/users", body={"workspace": self._workspace}
        )
        return parse_obj_as(List[UserStats], r)

    def get_user_stats_for_entry(self, entry_id: str) -> List[UserStats]:
        """Get a list of user stats for an entry

        Returns:
            List[UserStats]: List of user stats
        """
        r = self._make_request("get", f"/api/user/users/{entry_id}")
        return parse_obj_as(List[UserStats], r)

    def admin_get_users(self) -> List[User]:
        """Get all users

        Returns:
            List[User]: List of users
        """
        r = self._make_request("get", "/api/admin/users")
        return parse_obj_as(List[User], r)

    def admin_update_user(self, user_id: str, **kwargs) -> Dict[str, str]:
        """Update user attributes as an admin

        Args:
            user_id (str): User ID
            **admin (bool): If admin user
            **disabled (bool): Disable a user
            **avatar (str): Change user avatar
            **reset_api_key (bool): Reset the users API key

        Returns:
            Dict[str, str]: Updated user response
        """
        kwargs["user_id"] = user_id
        return self._make_request("post", "/api/admin/users", kwargs)

    def admin_delete_user(self, user_id: str) -> None:
        """Delete a user

        Args:
            user_id (str): User ID
        """
        body = {"user_id": user_id}
        self._make_request("delete", f"/api/admin/users", body)
        return None

    def admin_get_integrations(self) -> Dict[str, Any]:
        """Get all integrations

        Returns:
            Dict[str, Any]: Integrations
        """
        return self._make_request("get", "/api/admin/config")

    def admin_delete_workspace(self, workspace_id: str) -> None:
        """Delete a workspace

        Args:
            workspace_id (str): Workspace ID
        """
        body = {"workspace": workspace_id}
        self._make_request("delete", "/api/admin/entries", body)
        return None

    # def adminGetConfigSlack(self) -> Config:
    # TODO: Implement this
    #     """Get Slack config options

    #     Returns:
    #         Config: Config options
    #     """
    #     r = self._make_request("get", "/api/admin/config/slack")
    #     return Config(**r)

    # def adminGetConfigDiscord(self) -> Config:
    # TODO: Implement this
    #     """Get Discord config options

    #     Returns:
    #         Config: Config options
    #     """
    #     r = self._make_request("get", "/api/admin/config/discord")
    #     return Config(**r)

    # def adminSetConfigSlack(self, **kwargs) -> None:
    # TODO: Implement this
    #     """Configure a slack channel

    #     Args:
    #         enable (bool): Enable Slack threads
    #         workspaces (dict): Key is the workspace name and value is the channel
    #         token (str): Slack token with the valid oauth permissions

    #     Returns:
    #         None: None
    #     """
    #     return self._make_request("post", "/api/config/slack", kwargs)

    # def adminSetConfigDiscord(self, **kwargs) -> None:
    # TODO: Implement this
    #     """Configure a Discord channel

    #     Args:
    #         enable (bool): Enable Discord threads
    #         workspaces (dict): Key is the workspace name and value is the webhook

    #     Returns:
    #         None: None
    #     """
    #     return self._make_request("post", "/api/config/discord", kwargs)

    def admin_health_check(self) -> None:
        """Perform an admin health check

        Returns:
            None: None
        """
        self._make_request("get", "/api/admin", isJson=False)
        return None

    def admin_delete_all(self, verify: str) -> None:
        # TODO: Implement this
        raise NotImplementedError

    def admin_delete_commits(self, entry_id: str) -> None:
        """Delete all commits for an entry

        Args:
            entry_id (str): [description]
        """
        body = {"entry_id": entry_id, "workspace": self._workspace}
        self._make_request("delete", "/api/admin/commits", body)
        return None

    def admin_export_workspace(self, workspace: str) -> bytes:
        """Export a workspace

        Args:
            workspace (str): Workspace to export

        Returns:
            bytes: Exported workspace as a zip file.
        """
        r = self._make_request(
            "get", f"/api/admin/workspaces/{workspace}", isJson=False
        )
        return r

    def admin_import_workspace_json(self, body: str) -> None:
        # TODO: Implement this
        raise NotImplementedError

    def admin_import_workspace_zip(self, body: bytes) -> None:
        # TODO: Implement this
        raise NotImplementedError

    def admin_delete_empty_workspaces(self) -> None:
        """Delete all empty workspaces"""
        self._make_request("delete", "/api/admin/workspaces", isJson=False)
        return None

    def admin_get_files(self) -> List[AdminFile]:
        """Get a list of instance files

        Returns:
            List[AdminFile]: List of files
        """
        res = self._make_request("get", "/api/admin/files")
        return parse_obj_as(List[AdminFile], res)

    def admin_get_workspace_files(self) -> List[AdminFile]:
        """Get a list of workspace files

        Returns:
            List[AdminFile]: List of files
        """
        res = self._make_request("get", f"/api/admin/files/{self._workspace}")
        return parse_obj_as(List[AdminFile], res)

    def admin_delete_workspace_files(self) -> None:
        """Delete all workspace files"""
        self._make_request(
            "delete", f"/api/admin/files/{self._workspace}", isJson=False
        )
        return None

    def admin_download_workspace_files(self) -> bytes:
        """Download all workspace files

        Returns:
            bytes: Zip file of workspace files
        """
        res = self._make_request(
            "get", f"/api/admin/files/{self._workspace}/download", isJson=False
        )
        return res

    def admin_delete_file(self, key: str) -> None:
        """Delete a file from the instance

        Args:
            key (str): Key for file
        """
        body = {"key": key}
        self._make_request("delete", "/api/admin/files", body, isJson=False)
        return None

    def admin_add_service_account(self, service_name: str) -> User:
        """Create a service account

        Args:
            service_name (str): Service name

        Returns:
            User: User object
        """
        body = {"username": service_name}
        res = self._make_request("put", "/api/admin/users/service", body)
        return parse_obj_as(User, res)

    def admin_get_service_accounts(self) -> List[ServiceAccount]:
        """Get a list of service accounts

        Returns:
            List[ServiceAccount]: List of service accounts
        """
        res = self._make_request("get", "/api/admin/users/service", isJson=False)
        return parse_obj_as(List[ServiceAccount], res)

    def admin_delete_service_account(self, id: str) -> None:
        """Delete a service account

        Args:
            id (str): Service account ID
        """
        body = {"id": id}
        self._make_request("delete", "/api/admin/users/service", body)
        return None

    def admin_delete_all_service_accounts(self) -> None:
        """Delete all service accounts"""
        self._make_request("patch", "/api/admin/users/service", isJson=False)
        return None

    def admin_archive_workspace(self) -> Dict[str, Any]:
        """Archive a workspace

        Returns:
            Dict[str, Any]: Workspace archive counts
        """
        body = {"workspace": self._workspace}
        res = self._make_request("post", f"/api/admin/archive/workspaces", body)
        return res

    def admin_archive_delete_commits(self) -> Dict[str, Any]:
        """Delete all commits for an archived workspace

        Returns:
            Dict[str, Any]: Workspace archive counts
        """
        body = {"workspace": self._workspace}
        res = self._make_request("delete", f"/api/admin/archive/workspaces", body)
        return res

    def admin_reset_cache(self) -> None:
        """Reset the cache"""
        self._make_request("delete", "/api/admin/cache", isJson=False)
        return None

    def admin_get_backups(self) -> List[Backup]:
        """Get a list of backups

        Returns:
            List[Backup]: List of backups
        """
        res = self._make_request("get", "/api/admin/workspaces/backups")
        return parse_obj_as(List[Backup], res)

    def admin_load_local_backup(self, backup_file: str) -> None:
        """Load a local backup

        Args:
            backup_file (str): Backup file
        """
        body = {"key": backup_file}
        self._make_request("put", "/api/admin/workspaces/backups", body, isJson=False)
        return None

    def admin_get_backup_file(self, key: str) -> bytes:
        """Get a backup file

        Args:
            key (str): Backup file key

        Returns:
            bytes: Backup file as a zip file
        """
        body = {"key": key}
        res = self._make_request(
            "get", f"/api/admin/workspaces/backups", body, isJson=False
        )
        return res

    def admin_delete_backup_file(self, key: str) -> None:
        """Delete a backup file

        Args:
            key (str): Backup file key
        """
        body = {"key": key}
        self._make_request(
            "delete", f"/api/admin/workspaces/backups", body, isJson=False
        )
        return None

    def admin_search_get_indexes(self) -> List[str]:
        """Get a list of search indexes

        Returns:
            List[str]: List of search indexes
        """
        res = self._make_request("get", "/api/admin/workspaces/search")
        return parse_obj_as(List[str], res)

    def admin_search_delete_index(self, index: str) -> None:
        """Delete a search index

        Args:
            index (str): Search index to delete
        """
        body = {"index": index}
        self._make_request("delete", "/api/admin/workspaces/search", body, isJson=False)
        return None

    def admin_search_index_workspace(self, workspace: str) -> None:
        """Index a workspace

        Args:
            workspace (str): Workspace to index
        """
        body = {"workspace": workspace}
        self._make_request("post", "/api/admin/workspaces/search", body, isJson=False)
        return None

    def admin_lock_workspace(self) -> None:
        # TODO: Implement
        raise NotImplementedError

    def admin_unlock_workspace(self) -> None:
        # TODO: Implement
        raise NotImplementedError

    def admin_workspace_public(self) -> None:
        # TODO: Implement
        raise NotImplementedError

    def admin_workspace_private(self) -> None:
        # TODO: Implement
        raise NotImplementedError

    def fileDownload(self, hash: str, out_path: str) -> None:
        """Download a file by hash

        Args:
            hash (str): Hash of file
            out_path (str): Outpath path to write file into
        """
        # TODO: Implement this
        # with open(out_path, "w") as f:
        #     b = self._make_request("get", "/api/files/{}".format(hash), None, False)
        #     f.write(b)
        return

    def fileUpload(self, entry_id: str, file_path: str) -> Commit:
        # TODO
        # url = urljoin(self.host, '/api/entry/{}/commit'.format(entry_id))
        # req = Request(
        #     method='PUT',
        #     url=url,
        #     data=open(str(Path().expanduser() / file_path), 'rb'),
        #     headers={"x-api-key": self.api_key},
        # )
        # try:
        #     res = urlopen(req)
        #     body = res.read().decode()
        #     self.status = res.getcode()
        #     if self.status > 300:
        #         raise BadResponse(self.status, res)
        #     return Commit(**loads(body))
        # except HTTPError as e:
        #     raise BadResponse(e.code, e.read())
        pass

    def get_entries(self) -> List[Entry]:
        """Get an array of all entries for a workspace

        Returns:
            List[Entry]: Array of entries
        """
        r = self._make_request("get", f"/api/entry/{self._workspace}")
        return parse_obj_as(List[Entry], r)

    def add_entry(self, title: str, category: str, **kwargs) -> Entry:
        """Create an entry

        Args:
            title (str): Entry title
            category (str): Entry category
            **piority (str): Priority of entry
            **tags (List[str]): Tags for entry

        Returns:
            Entry: New entry response
        """
        kwargs["title"] = title
        kwargs["category"] = category
        r = self._make_request("post", f"/api/entry/{self._workspace}", kwargs)
        return Entry(**r)

    def batch_add_entries(self, entries: List[Dict[str, str]]) -> None:
        """Create a batch of entries. Valid parameters are:
            title (str): Entry title
            category (str): Entry category
            piority (str): Priority of entry

        Args:
            entries (List[Dict[str, str]]): List of entries to create
        """
        body = entries
        self._make_request("put", f"/api/entry/{self._workspace}", body)
        return None

    def batch_delete_entries(self, entry_ids: List[str]) -> None:
        """Delete a batch of entries

        Args:
            entry_ids (List[str]): List of entry ids to delete
        """
        body = entry_ids
        self._make_request("delete", f"/api/entry/{self._workspace}", body)
        return None

    def get_entry(self, entry_id: str) -> Entry:
        """Get a specific entry

        Args:
            entry_id (str): Entry id

        Returns:
            Entry: An entry
        """
        r = self._make_request("get", f"/api/entry/{self._workspace}/{entry_id}")
        return Entry(**r)

    def update_entry(self, entry_id: str, **kwargs) -> Entry:
        """Update an entry

        Args:
            entry_id (str): Entry ID
            title (str): Entry title
            priority (str): Entry priority
            category (str): Entry category
            entry_tags (List[str]): Entry tags

        Returns:
            Entry: [description]
        """
        r = self._make_request(
            "post", f"/api/entry/{self._workspace}/{entry_id}", kwargs
        )
        return Entry(**r)

    def delete_entry(self, entry_id: str) -> Dict[str, int]:
        """Delete an entry and all of its corresponding data

        Args:
            entry_id (str): A valid entry id

        Returns:
            Dict[str, int]: Count of deleted items for an entry
        """
        return self._make_request("delete", f"/api/entry/{self._workspace}/{entry_id}")

    def get_entry_activities(self, entry_id: str, limit: int = 10) -> List[Activity]:
        """Get an entries activities

        Args:
            entry_id (str): A valid entry ID
            limit (int, optional): Number of activities to get. Defaults to 10.

        Returns:
            List[Activity]: List of activities
        """
        query = {"limit": limit}
        res = self._make_request(
            "get", f"/api/misc/activity/{entry_id}", queryParams=query
        )
        return parse_obj_as(List[Activity], res)

    def add_commit(self, entry_id: str, title: str, data: Any, **kwargs) -> Commit:
        """Add a commit to an entry

        Args:
            entry_id (str): Entry id to add to
            title (str): Title of commit
            data (str): Data for commit
            meta (dict): Meta options. Defaults to {}

        Returns:
            Commit: The commit created
        """
        kwargs["title"] = title
        kwargs["type"] = self.commit_type
        kwargs["data"] = data
        r = self._make_request(
            "post", f"/api/entry/{self.workspace}/{entry_id}/commit", kwargs
        )
        return Commit(**r)

    def commit_add_execute(self, entry_id: str, command: str) -> Commit:
        """Execute a command and add output as a commit

        Args:
            entry_id (str): Valid entry id
            command (str): Command to execute

        Returns:
            Commit: The commit created
        """
        output = getoutput(command)
        body = {"title": command, "data": output, "type": "stdout"}
        r = self._make_request(
            "post", f"/api/entry/{self.workspace}/{entry_id}/commit", body
        )
        return Commit(**r)

    def commit_add_code_self(self, entry_id: str) -> Commit:
        """Add the script this is called on as a commit

        Args:
            entry_id (str): Entry id

        Returns:
            Commit: The commit created
        """
        path = sys.argv[0]
        with open(path, "r") as f:
            data = f.read()
            file_name = Path(path).parts[-1]
            body = {"data": data, "title": file_name, "type": self.commit_type}
            r = self._make_request(
                "post", f"/api/entry/{self.workspace}/{entry_id}/commit", body
            )
            return Commit(**r)

    def get_commit(self, entry_id: str, commit_id: str) -> Commit:
        """Get a specific commit

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id

        Returns:
            Commit: The commit requested
        """
        r = self._make_request(
            "get", f"/api/entry/{self.workspace}/{entry_id}/commit/{commit_id}"
        )
        return Commit(**r)

    def batch_add_commit(self, entry_id: str, commit: List[Dict[str, str]]) -> None:
        """Batch add commits

        Args:
            entry_id (str): A valid entry ID
            commit (List[Dict[str, str]]): A list of valid commits. Valid paramets are:
                title (str): Commit title
                data (str): Commit data
                type (str): Commit type
        """
        body = commit
        self._make_request(
            "post", f"/api/entry/{self.workspace}/{entry_id}/commits", body
        )
        return None

    def delete_commit(self, entry_id: str, commit_id: str) -> Commit:
        """Delete a a commit

        Args:
            entry_id (str): A valid entry ID
            commit_id (str): A valid commit ID

        Returns:
            Commit: The commit deleted
        """
        r = self._make_request(
            "delete", f"/api/entry/{self._workspace}/{entry_id}/commit/{commit_id}"
        )
        return Commit(**r)

    def update_commit(self, entry_id: str, commit_id: str, **kwargs) -> Commit:
        """Update a commit

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id
            title (str): Commit title
            marked (bool): Mark a commit
            locked (bool): Lock a commit
            meta (dict): Meta options

        Returns:
            Commit: The updated commit
        """
        r = self._make_request(
            "post", f"/api/entry/{self.workspace}/{entry_id}/commit/{commit_id}", kwargs
        )
        return Commit(**r)

    def star_commit(self, entry_id: str, commit_id: str, mark: bool) -> Commit:
        """Mark a commit

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id
            marked (bool): Mark a commit

        Returns:
            Commit: The updated commit
        """
        body = {"marked": mark}
        r = self._make_request(
            "post", f"/api/entry/{self.workspace}/{entry_id}/commit/{commit_id}", body
        )
        return Commit(**r)

    def lock_commit(self, entry_id: str, commit_id: str, lock: bool) -> Commit:
        """Lock/Unlock a commit

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id
            locked (bool): Lock a commit

        Returns:
            Commit: The updated commit
        """
        body = {"locked": lock}
        r = self._make_request(
            "post", f"/api/entry/{self.workspace}/{entry_id}/commit", body
        )
        return Commit(**r)

    def get_commit_likes(self, entry_id: str, commit_id: str) -> List[Like]:
        """Get all likes for a commit

        Args:
            entry_id (str): Entry ID
            commit_id (str): Commit ID

        Returns:
            List[Like]: List of likes
        """
        res = self._make_request(
            "get", f"/api/entry/{self.workspace}/{entry_id}/commit/{commit_id}/likes"
        )
        return parse_obj_as(List[Like], res)

    def add_commit_like(self, entry_id: str, commit_id: str) -> Dict[str, Any]:
        """Get all likes for a commit

        Args:
            entry_id (str): Entry ID
            commit_id (str): Commit ID

        Returns:
            Dict[str, Any]: List of likes
        """
        res = self._make_request(
            "post", f"/api/entry/{self.workspace}/{entry_id}/commit/{commit_id}/likes"
        )
        return res

    def delete_commit_like(self, entry_id: str, commit_id: str) -> Dict[str, Any]:
        """Get all likes for a commit

        Args:
            entry_id (str): Entry ID
            commit_id (str): Commit ID
            like_id (str): Like ID

        Returns:
            None
        """
        res = self._make_request(
            "delete", f"/api/entry/{self.workspace}/{entry_id}/commit/{commit_id}/likes"
        )
        return res

    def get_file(self, file_hash: str) -> bytes:
        """Get a file from the repo

        Args:
            file_hash (str): A valid file file_hash

        Returns:
            bytes: The file requested
        """
        r = self._make_request("get", f"/api/file/{file_hash}")
        return r

    def get_commit_tags(self, entry_id: str, commit_id: str) -> List[CommitTag]:
        """Get all tags for a commit

        Args:
            entry_id (str): Entry ID
            commit_id (str): Commit ID

        Returns:
            List[Tag]: List of tags
        """
        res = self._make_request(
            "get", f"/api/entry/{self.workspace}/{entry_id}/tag/{commit_id}"
        )
        return parse_obj_as(List[CommitTag], res)

    def add_commit_tag(self, entry_id: str, commit_id: str, tag: str) -> None:
        """Get all tags for a commit

        Args:
            entry_id (str): Entry ID
            commit_id (str): Commit ID
            tag (str): Tag text

        Returns:
            List[Tag]: List of tags
        """
        body = {"text": tag}
        res = self._make_request(
            "post",
            f"/api/entry/{self.workspace}/{entry_id}/tag/{commit_id}",
            body,
            isJson=False,
        )
        return None

    def delete_commit_tag(self, entry_id: str, commit_id: str, tag_id: str) -> None:
        """Get all tags for a commit

        Args:
            entry_id (str): Entry ID
            commit_id (str): Commit ID
            tag_id (str): Tag ID

        Returns:
            List[Tag]: List of tags
        """
        body = {"tag_id": tag_id}
        res = self._make_request(
            "delete",
            f"/api/entry/{self.workspace}/{entry_id}/tag/{commit_id}",
            body,
            isJson=False,
        )
        return None

    def add_description(self, entry_id: str, text: str) -> Description:
        """Add or update a description to an entry

        Args:
            entry_id (str): entry id
            text (str): Notice text

        Returns:
            Description: The description object
        """
        body = {"text": text}
        r = self._make_request(
            "post", f"/api/entry/{self._workspace}/{entry_id}/description", body
        )
        return Description(**r)

    def delete_description(self, entry_id: str) -> None:
        """Delete a description

        Args:
            entry_id (str): A valid entry id

        Returns:
            None: None
        """
        return self._make_request(
            "delete",
            f"/api/entry/{self._workspace}/{entry_id}/description",
            isJson=False,
        )

    def get_commit_comments(self, entry_id: str, commit_id: str) -> List[Description]:
        """Get all comments

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id

        Returns:
            List[Description]: An array of comments
        """
        r = self._make_request(
            "get", f"/api/entry/{self._workspace}/{entry_id}/commit/{commit_id}/comment"
        )
        return parse_obj_as(List[Description], r)

    def add_commit_comment(
        self, entry_id: str, commit_id: str, text: str
    ) -> Description:
        """Add a comment to a commit

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id
            text (str): Comment text

        Returns:
            Description: Added comment object
        """
        body = {"text": text}
        r = self._make_request(
            "post",
            "/api/entry/{self._workspace}/{entry_id}/commit/{commit_id}/comment",
            body,
        )
        return Description(**r)

    def delete_commit_comment(
        self, entry_id: str, commit_id: str, comment_id: str
    ) -> None:
        """Delete a comment

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id

        Returns:
            None: None
        """
        body = {"comment_id": comment_id}
        r = self._make_request(
            "delete",
            f"/api/entry/{self._workspace}/{entry_id}/commit/{commit_id}/comment",
            body,
            isJson=False,
        )
        return None

    def get_notes(self, entry_id: str, commit_id: str = None) -> List[Note]:
        """Get an array of all notes for an entry. If commit_id is specified,
        only notes for that reference that commit are returned.

        Args:
            entry_id (str): A valid entry ID
            commit_id (str, optional): A valid commit ID. Defaults to None.

        Returns:
            List[Note]: List of notes
        """
        query = {}
        if commit_id:
            query["commit_id"] = commit_id
        r = self._make_request(
            "get",
            f"/api/entry/{self._workspace}/{entry_id}/notes",
            None,
            queryParams=query,
        )
        return parse_obj_as(List[Note], r)

    def delete_note(self, entry_id: str, note_id: str) -> None:
        """Delete a note

        Args:
            entry_id (str): A valid entry id
            note_id (str): A valid note id

        Returns:
            None: None
        """
        body = {"note_id": note_id}
        r = self._make_request(
            "delete", f"/api/entry/{self._workspace}/{entry_id}/notes", body, False
        )
        return None

    def add_note(self, entry_id: str, text: str, commit_id: str = None) -> None:
        """Add a new note to an entry

        Args:
            entry_id (str): A valid entry id
            text (str): Note text. Min 2, max 1000
            commit_id (str): Optional commit id to reference.

        Returns:
            None: None
        """
        body = {"text": text}
        if commit_id:
            body["commit_id"] = commit_id
        r = self._make_request(
            "post", f"/api/entry/{self._workspace}/{entry_id}/notes", body, False
        )
        return None

    def update_note(self, entry_id: str, note_id: str, text: str) -> None:
        """Update an existing note

        Args:
            entry_id (str): A valid entry id
            note_id (str): A valid notes id
            text (str): Updated note title

        Returns:
            None: None
        """
        body = {"text": text, "note_id": note_id}
        r = self._make_request(
            "patch", f"/api/entry/{self._workspace}/{entry_id}/notes", body, False
        )
        return None

    def get_workspaces(self) -> List[Workspace]:
        """Get all workspaces

        Returns:
            List[Workspace]: List of workspaces
        """
        r = self._make_request("get", "/api/workspace")
        return parse_obj_as(List[Workspace], r)

    def update_workspace(self, **kwargs) -> None:
        """Update a workspace

        Args:
            kwargs (dict): Workspace properties. Valid properties are:
                description (str): Workspace description
                login (str): Workspace login
                password (str): Workspace password
                url (str): Workspace url

        Returns:
            None: None
        """
        body = {"workspace": kwargs}
        r = self._make_request(
            "post", f"/api/workspace/{self._workspace}", body, isJson=False
        )
        return None

    def search_archive(
        self, q: str, limit: int = 10, entry_id: str = None, category: str = None
    ) -> List[Hit]:
        """Search the archive

        Args:
            q (str): What to search for
            limit (int, optional): Limit results. Defaults to 10.
            entry_id (str, optional): Search for specific entry id. Defaults to None.
            category (str, optional): Limit search to specific category. Defaults to None.

        Returns:
            List[Hit]: List of hits
        """
        query = {"query": q, "limit": limit}
        if entry_id:
            query["entry_id"] = entry_id
        if category:
            query["category"] = category
        res = self._make_request("get", "/api/archive/search", queryParams=query)
        return parse_obj_as(List[Hit], res)

    def search_workspace(
        self, q: str, limit: int = 10, entry_id: str = None, category: str = None
    ) -> List[Hit]:
        """Search a specific workspace

        Args:
            q (str): What to search for
            limit (int, optional): Limit results. Defaults to 10.
            entry_id (str, optional): Search for specific entry id. Defaults to None.
            category (str, optional): Limit search to specific category. Defaults to None.

        Returns:
            List[Hit]: List of hits
        """
        query = {"query": q, "limit": limit}
        if entry_id:
            query["entry_id"] = entry_id
        if category:
            query["category"] = category
        res = self._make_request(
            "get", f"/api/archive/search/{self._workspace}", queryParams=query
        )
        if res is None:
            return []
        return parse_obj_as(List[Hit], res)

    def get_flags(self, entry_id: str) -> List[Flag]:
        """Get all flags for an entry

        Args:
            entry_id (str): A valid entry id

        Returns:
            List[Flag]: List of flags
        """
        r = self._make_request("get", f"/api/entry/{self._workspace}/{entry_id}/flags")
        return parse_obj_as(List[Flag], r)

    def delete_flag(self, entry_id: str, flag_id: str) -> None:
        """Delete a flag

        Args:
            entry_id (str): A valid entry id
            flag_id (str): A valid flag id

        Returns:
            None: None
        """
        body = {"flag_id": flag_id}
        r = self._make_request(
            "delete", f"/api/entry/{self._workspace}/{entry_id}/flags", body, False
        )
        return None

    def add_flag(self, entry_id: str, flag: str) -> None:
        """Add a new flag to an entry

        Args:
            entry_id (str): A valid entry id

        Returns:
            None: None
        """
        body = {"flag": flag}
        r = self._make_request(
            "post", f"/api/entry/{self._workspace}/{entry_id}/flags", body, False
        )
        return None
