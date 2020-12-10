import sys
from mixto.types.entry import Commit, Description, Entry
from mixto.types.misc import Config, NoticeTypes
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urljoin
from pathlib import Path
from json import dumps, loads
from subprocess import getoutput
from typing import Any, Dict, List, Union
from .exceptions import BadResponse
from .types.user import Settings, UserInfo, Version


class Mixto:
    def __init__(self, host: str = None, api_key: str = None) -> None:
        super().__init__()
        self.host = host
        self.api_key = api_key
        self.status = None

        if self.host == None or self.api_key == None:
            try:
                conf_path = str(Path().home() / ".mixto.json")
                with open(conf_path) as f:
                    j = loads(f.read())
                    self.host = j["host"]
                    self.api_key = j["api_key"]
            except:
                print("Cannot read Mixto config")

    def _make_request(
        self, method: str, uri: str, body: Dict[str, str] = {}, isJson: bool = True
    ) -> Union[Dict[str, Any], None]:
        url = urljoin(self.host, uri)
        req = Request(
            method=method.upper(),
            url=url,
            data=dumps(body).encode(),
            headers={"x-api-key": self.api_key},
        )
        if body:
            req.add_header("Content-Type", "application/json")
        try:
            res = urlopen(req)
            body = res.read().decode()
            self.status = res.getcode()
            if self.status > 300:
                raise BadResponse(self.status, res)
            if isJson:
                return loads(body)
            else:
                return body
        except HTTPError as e:
            raise BadResponse(e.code, e.read())

    def miscApiVersion(self) -> Version:
        """Get app version information

        Returns:
            Version: App version information
        """
        r = self._make_request("get", "/api/misc")
        return Version(**r)

    def miscCategories(self) -> List[str]:
        """Get a list of valid categories

        Returns:
            List[str]: List of categories
        """
        return self._make_request("get", "/api/misc/categories")

    def miscGetWorkspaces(self) -> List[str]:
        """Get a list of available workspaces

        Returns:
            List[str]: List of workspaces
        """
        return self._make_request("get", "/api/misc/workspaces")

    def userInfo(self) -> UserInfo:
        """Get user info

        Returns:
            UserInfo: User info
        """
        return UserInfo(**self._make_request("get", "/api/user"))

    def userResetApiKey(self) -> Dict[str, str]:
        """Reset user api key

        Returns:
            Dict[str ,str]: Contains ``new_api_key`` and ``old_api_key``
        """
        return self._make_request("get", "/api/user/reset")

    def userGetSettings(self) -> Dict[str, str]:
        """Get a dict of current user settings

        Returns:
            Dict[str, str]: User settings dict
        """
        return self._make_request("get", "/api/user/settings")

    def userSetSettings(self, **body) -> Settings:
        """Set a users settings

        Args:
            dark_theme (bool): Enable or disable dark theme

        Returns:
            Settings: New settings
        """
        r = self._make_request("post", "/api/user/settings", body)
        return Settings(**r)

    def adminGetUsers(self) -> List[UserInfo]:
        """Get all users as admin

        Returns:
            List[UserInfo]: List of users
        """
        r = self._make_request("get", "/api/admin/users")
        return [UserInfo(**u) for u in r]

    def adminUpdateUser(self, user_id: str, **kwargs) -> Dict[str, str]:
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
        return self._make_request("post", "post", "/api/admin/users", kwargs)

    def adminGetConfigSlack(self) -> Config:
        """Get Slack config options

        Returns:
            Config: Config options
        """
        r = self._make_request("get", "/admin/config/slack")
        return Config(**r)

    def adminGetConfigDiscord(self) -> Config:
        """Get Discord config options

        Returns:
            Config: Config options
        """
        r = self._make_request("get", "/admin/config/discord")
        return Config(**r)

    def adminSetConfigSlack(self, **kwargs) -> None:
        """Configure a slack channel

        Args:
            enable (bool): Enable Slack threads
            channel (str): Slack channel to post on
            token (str): Slack token with the valid oauth permissions

        Returns:
            None: None
        """
        return self._make_request("post", "/api/config/slack", kwargs)

    def adminSetConfigDiscord(self, **kwargs) -> None:
        """Configure a Discord channel

        Args:
            enable (bool): Enable Discord threads
            webhook (str): Discord channel webhook

        Returns:
            None: None
        """
        return self._make_request("post", "/api/config/discord", kwargs)

    def fileDownload(self, hash: str, out_path: str) -> None:
        """Download a file by hash

        Args:
            hash (str): Hash of file
            out_path (str): Outpath path to write file into
        """
        with open(out_path, "w") as f:
            b = self._make_request("get", "/api/files/{}".format(hash), None, False)
            f.write(b)
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

    def adminDeleteWorkspace(self, workspace: str) -> Dict[str, Any]:
        """Delete a workspace and all its entries

        Args:
            workspace (str): A valid workspace

        Returns:
            Dict[str, Any]: A dict of the response
        """
        body = {"workspace": workspace}
        return self._make_request("delete", "/api/admin/entries", body)

    def entryGetAll(self) -> List[Entry]:
        """Get an array of all entries

        Returns:
            List[Entry]: Array of entries
        """
        r = self._make_request("get", "/api/entry")
        return [Entry(**i) for i in r]

    def entryCreate(self, title: str, category: str, **kwargs) -> Entry:
        """Create an entry

        Args:
            title (str): Entry title
            category (str): Entry category
            piority (str): Priority of entry
            workspace (str): Workspace for entry

        Returns:
            Entry: New entry response
        """
        kwargs["title"] = title
        kwargs["category"] = category
        r = self._make_request("post", "/api/entry", kwargs)
        return Entry(**r)

    def entryGet(self, entry_id: str) -> Entry:
        """Get a specific entry

        Args:
            entry_id (str): Entry id

        Returns:
            Entry: An entry
        """
        r = self._make_request("get", "/api/entry/{}".format(entry_id))
        return Entry(**r)

    def entryUpdate(self, entry_id: str, **kwargs) -> Entry:
        """Update an entry

        Args:
            entry_id (str): Entry ID
            title (str): Entry title
            priority (str): Entry priority
            category (str): Entry category
            workspace (str): Entry workspace

        Returns:
            Entry: [description]
        """
        r = self._make_request("post", "/api/entry/{}".format(entry_id))
        return Entry(**r)

    def entryDelete(self, entry_id: str) -> None:
        """Delete an entry and all of its corresponding data

        Args:
            entry_id (str): A valid entry id

        Returns:
            None: OK on success
        """
        return self._make_request("delete", "/api/entry/{}".format(entry_id))

    def commitAdd(self, entry_id: str, title: str, data: Any, **kwargs) -> Commit:
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
        kwargs["type"] = "dump"
        kwargs["data"] = data
        r = self._make_request("post", "/api/entry/{}/commit".format(entry_id), kwargs)
        return Commit(**r)

    def commitAddCommand(self, entry_id: str, command: str) -> Commit:
        """Execute a command and add output as a commit

        Args:
            entry_id (str): Valid entry id
            command (str): Command to execute

        Returns:
            Commit: The commit created
        """
        output = getoutput(command)
        body = {"title": command, "data": output, "type": "stdout"}
        r = self._make_request("post", "/api/entry/{}/commit".format(entry_id), body)
        return Commit(**r)

    def commitAddScript(self, entry_id: str) -> Commit:
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
            body = {"data": data, "title": file_name, "type": "script"}
            r = self._make_request(
                "post", "/api/entry/{}/commit".format(entry_id), body
            )
            return Commit(**r)

    def commitGet(self, entry_id: str, commit_id: str) -> Commit:
        """Get a specific commit

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id

        Returns:
            Commit: The commit requested
        """
        r = self._make_request(
            "get", "/api/entry/{}/commit{}".format(entry_id, commit_id)
        )
        return Commit(**r)

    def commitDelete(self, entry_id: str, commit_id: str) -> Commit:
        """Delete a a commit

        Args:
            entry_id (str): A valid entry ID
            commit_id (str): A valid commit ID

        Returns:
            Commit: The commit deleted
        """
        r = self._make_request(
            "delete", "/api/entry/{}/commit/{}".format(entry_id, commit_id)
        )
        return Commit(**r)

    def commitUpdate(self, entry_id: str, commit_id: str, **kwargs) -> Commit:
        """Update a commit

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id
            title (str): Commit title
            marked (bool): Mark a commit
            meta (dict): Meta options

        Returns:
            Commit: The updated commit
        """
        r = self._make_request(
            "post", "/api/entry/{}/commit/{}".format(entry_id, commit_id), kwargs
        )
        return Commit(**r)

    def commitMark(self, entry_id: str, commit_id: str, mark: bool) -> Commit:
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
            "post", "/api/entry/{}/commit/{}".format(entry_id, commit_id), body
        )
        return Commit(**r)

    def noticeUpdate(
        self, entry_id: str, text: str, priority: NoticeTypes = "default"
    ) -> Description:
        """Add or update a notice to an entry

        Args:
            entry_id (str): entry id
            text (str): Notice text
            priority (NoticeTypes, optional): Notice priority. Defaults to 'default'.

        Returns:
            Description: The notice object
        """
        body = {"text": text, "priority": priority}
        r = self._make_request("post", "/api/entry/{}/notice".format(entry_id), body)
        return Description(**r)

    def noticeDelete(self, entry_id: str) -> None:
        """Delete a notice

        Args:
            entry_id (str): A valid entry id

        Returns:
            None: None
        """
        return self._make_request(
            "delete", "/api/entry/{}/notice".format(entry_id), None, False
        )

    def descriptionUpdate(self, entry_id: str, text: str) -> Description:
        """Add or update a description to an entry

        Args:
            entry_id (str): entry id
            text (str): Notice text

        Returns:
            Description: The description object
        """
        body = {"text": text}
        r = self._make_request(
            "post", "/api/entry/{}/description".format(entry_id), body
        )
        return Description(**r)

    def descriptionDelete(self, entry_id: str) -> None:
        """Delete a description

        Args:
            entry_id (str): A valid entry id

        Returns:
            None: None
        """
        return self._make_request(
            "delete", "/api/entry/{}/description".format(entry_id), None, False
        )

    def commentsGet(self):
        # TODO
        pass

    def commentsAdd(self):
        # TODO
        pass

    def commentsDelete(self):
        # TODO
        pass

    def chatGet(self):
        # TODO
        pass

    def chatAdd(self):
        # TODO
        pass

    def chatDelete(self):
        # TODO
        pass
