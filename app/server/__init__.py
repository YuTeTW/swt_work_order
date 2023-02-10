from enum import Enum


class StaffStatus(Enum):
    resign = 0
    is_work = 1


class ClientStatus(Enum):
    not_cooperate = 0
    cooperate = 1
