import sys

from typing_extensions import Literal
from mixto.types.entry import Commit, Description, Entry, Note
from mixto.types.misc import CommitTypes, Config, NoticeTypes, Workspace
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urljoin, urlencode
from pathlib import Path
from json import dumps, loads
from subprocess import getoutput
from typing import Any, Dict, List, Optional, Union
from .exceptions import BadResponse
from .types.user import Settings, UserInfo, Version

from .__version__ import __version__


class Mixto:
    def __init__(self, host: str = None, api_key: str = None) -> None:
        super().__init__()
        self.host: Optional[str] = host
        self.api_key: Optional[str] = api_key
        self.status: int = 0
        self.commit_type: CommitTypes = "script"

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
        self,
        method: str,
        uri: str,
        body: Union[Dict[str, Any], None] = {},
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
            body = res.read().decode()
            self.status = res.getcode()
            if self.status > 300:
                raise BadResponse(self.status, res)
            if isJson:
                return loads(str(body))
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

    def miscGetWorkspaces(self) -> List[Workspace]:
        """Get a list of available workspaces

        Returns:
            List[str]: List of workspaces
        """
        r = self._make_request("get", "/api/misc/workspaces")
        return [Workspace(**e) for e in r]

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
        return self._make_request("post", "/api/admin/users", kwargs)

    def adminGetConfigSlack(self) -> Config:
        """Get Slack config options

        Returns:
            Config: Config options
        """
        r = self._make_request("get", "/api/admin/config/slack")
        return Config(**r)

    def adminGetConfigDiscord(self) -> Config:
        """Get Discord config options

        Returns:
            Config: Config options
        """
        r = self._make_request("get", "/api/admin/config/discord")
        return Config(**r)

    def adminSetConfigSlack(self, **kwargs) -> None:
        """Configure a slack channel

        Args:
            enable (bool): Enable Slack threads
            workspaces (dict): Key is the workspace name and value is the channel
            token (str): Slack token with the valid oauth permissions

        Returns:
            None: None
        """
        return self._make_request("post", "/api/config/slack", kwargs)

    def adminSetConfigDiscord(self, **kwargs) -> None:
        """Configure a Discord channel

        Args:
            enable (bool): Enable Discord threads
            workspaces (dict): Key is the workspace name and value is the webhook

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
        r = self._make_request(
            "get", "/api/entry/{}".format(entry_id), queryParams={"all": "true"}
        )
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
        kwargs["type"] = self.commit_type
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
            body = {"data": data, "title": file_name, "type": self.commit_type}
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
            locked (bool): Lock a commit
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

    def commitLock(self, entry_id: str, commit_id: str, lock: bool) -> Commit:
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

    def commentsGet(self, entry_id: str, commit_id: str) -> List[Description]:
        """Get all comments

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id

        Returns:
            List[Description]: An array of comments
        """
        r = self._make_request(
            "get", "/api/entry/{}/commit/{}/comment".format(entry_id, commit_id)
        )
        return [Description(**i) for i in r]

    def commentsAdd(self, entry_id: str, commit_id: str, text: str) -> Description:
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
            "post", "/api/entry/{}/commit/{}/comment".format(entry_id, commit_id), body
        )
        return Description(**r)

    def commentsDelete(self, entry_id: str, commit_id: str) -> None:
        """Delete a comment

        Args:
            entry_id (str): A valid entry id
            commit_id (str): A valid commit id

        Returns:
            None: None
        """
        r = self._make_request(
            "delete",
            "/api/entry/{}/commit/{}/comment".format(entry_id, commit_id),
            None,
            False,
        )
        return None

    def notesGet(self, entry_id: str) -> List[Note]:
        """Get an array of all user notes

        Args:
            entry_id (str): A valid entry ID

        Returns:
            List[Note]: List of notes
        """
        r = self._make_request("get", "/api/entry/{}/notes".format(entry_id), None)
        return [Note(**i) for i in r]

    def notesDelete(self, entry_id: str, notes_id: str) -> None:
        """Delete a note

        Args:
            entry_id (str): A valid entry id
            notes_id (str): A valid note id

        Returns:
            None: None
        """
        r = self._make_request(
            "delete", "/api/entry/{}/notes/{}".format(entry_id, notes_id), None, False
        )
        return None

    def notesAdd(self, entry_id: str, text: str, title: str) -> None:
        """Add a new note to an entry

        Args:
            entry_id (str): A valid entry id
            text (str): Note text. Min 2, max 1000
            title (str): Note title. Mix 2, max 80

        Returns:
            None: None
        """
        body = {'text': text, 'title': title}
        r = self._make_request(
            "post", "/api/entry/{}/notes".format(entry_id), body, False
        )
        return None

    def notesUpdate(self, entry_id: str, notes_id: str, text: str, title: str) -> None:
        """Update an existing note

        Args:
            entry_id (str): A valid entry id
            notes_id (str): A valid notes id
            text (str): Updated note title
            title (str): Updated note text

        Returns:
            None: None
        """
        body = {text: text, title: title}
        r = self._make_request(
            "post", "/api/entry/{}/notes/{}".format(entry_id, notes_id), body, False
        )
        return None

    def chatGet(self):
        # TODO
        raise NotImplemented

    def chatAdd(self):
        # TODO
        raise NotImplemented

    def chatDelete(self):
        # TODO
        raise NotImplemented
