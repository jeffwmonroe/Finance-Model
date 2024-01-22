from enum import Enum


class EventType(str, Enum):
    DNB = "DNB"
    NoTravel = "No Travel"
    Meeting = "Meeting"
    Training = "Training"
    Canceled = "Canceled"


class ClassLocation(str, Enum):
    InPerson = "In Person"
    Virtual = "Virtual"
