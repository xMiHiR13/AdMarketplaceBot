from typing import Dict

from MABot.types import CVars, ThreadSafeDict

CVARS = CVars()
CONVERSATIONS: Dict[int, int] = ThreadSafeDict()
CONVERSATIONS_LAST_ACTIVITY: Dict[str, int] = ThreadSafeDict()
CONVERSATIONS_NOTIFICATION: Dict[str, int] = ThreadSafeDict()
