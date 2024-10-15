from datetime import datetime, timedelta, timezone
from cat.utils import singleton
from cat.log import log

from cat.auth.permissions import AuthUserInfo


@singleton
class SessionManager:
    """
    This class is responsible for strays session management

    - adding new sessions
    - expiring sessions
    """

    def __init__(self, strays: any) -> None:
        self.strays = strays
        self.sessions = {}

    def add_or_refresh(self, user: AuthUserInfo, minutes: int = 60 * 24) -> None:
        """
        add new session setting expiration time to now plus x minutes
        each session uses the expiration time as key and the value is a dict with user_id and stray
        """

        current_time = datetime.now(timezone.utc) + timedelta(minutes=minutes)

        # if user_id is already in the session we removed it first
        for timestamp in self.sessions:
            if self.sessions[timestamp]["user_id"] == user.id:
                self.sessions.pop(timestamp)
                break

        # then we create a new session
        self.sessions[current_time] = {"user_id": user.id, "name": user.name}
        pass

    def evict_expired_sessions(self) -> int:
        """
        this method removes expired sessions
        """

        log.info("active sessions:")
        log.info("*" * 20)

        time_limit = datetime.now(timezone.utc)

        for timestamp in self.sessions:
            if timestamp >= time_limit:
                log.info(f"expiration date: {timestamp} -> {self.sessions[timestamp]}")
        log.info("*" * 20)

        # retrieve all expired sessions
        keys_to_remove = [
            timestamp for timestamp in self.sessions if timestamp < time_limit
        ]

        # for each expired session key
        for key in keys_to_remove:
            # get the user_id
            user_id = self.sessions[key]["user_id"]
            if user_id in self.strays.keys():
                log.info(
                    f"deleting expired user: {self.strays[user_id].user_id} user_id: {user_id}"
                )

                # remove the users' stray
                del self.strays[user_id]

            # then remove the session using the key (timestamp)
            self.sessions.pop(key)

        expired_count = len(keys_to_remove)
        if expired_count > 0:
            log.info(f"{expired_count} sessions expired.")

        return expired_count
