from enum import Enum

class DealStatus(str, Enum):
    SCHEDULED = "scheduled"
    POSTED = "posted"
    COMPLETED = "completed"
    POSTING_FAILED = "posting_failed"
    REFUNDED_EDIT = "refunded_edit"
    REFUNDED_DELETE = "refunded_delete"
    CANCELLED = "cancelled"

    @classmethod
    def terminal_statuses(cls):
        return {
            cls.COMPLETED,
            cls.POSTING_FAILED,
            cls.REFUNDED_EDIT,
            cls.REFUNDED_DELETE,
            cls.CANCELLED,
        }

class DealRole(str, Enum):
    ADVERTISER = "advertiser"
    PUBLISHER = "publisher"
