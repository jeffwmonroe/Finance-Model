from haztrain_calendar.haztrain_calendar_enums import EventType, ClassLocation
from gcsa.event import Event


def event_type(summary: str) -> EventType:
    if summary[:3] == 'DNB' or summary[-3:] == 'DNB' or summary[-3:].lower() == "off":
        return EventType.DNB
    if summary[:2] == 'QM':
        return EventType.Meeting
    if 'QM' in summary:
        return EventType.Meeting
    if 'Q2M' in summary:
        return EventType.Meeting
    if 'Q4' in summary:
        return EventType.Meeting
    if 'kickoff meeting' in summary.lower():
        return EventType.Meeting
    if "cancelled" in summary.lower():
        return EventType.Canceled
    if summary[:4] == 'CANX':
        return EventType.Canceled
    if summary[:9] == 'Tentative':
        return EventType.Canceled
    if 'no travel' in summary.lower() or summary[:12].lower() == 'virtual only':
        return EventType.NoTravel

    return EventType.Training


def get_instructor(event: Event, inst_dict) -> str | None:
    instructor_sum = None
    instructor_attendee = None
    for inst in inst_dict.values():
        if inst.lower() in event.summary.lower():
            instructor_sum = inst
            break

    for attendee in event.attendees:
        if attendee.email == "haztraintraining@gmail.com":
            continue
        if attendee.email in inst_dict.keys():
            # print(f'attendee found: {attendee.email}, {inst_dict[attendee.email]}')
            instructor_attendee = inst_dict[attendee.email]
    if instructor_sum is None and instructor_attendee is None:
        # print(f'No instructor')
        return None
    if instructor_sum is None:
        return instructor_attendee
    if instructor_attendee is None:
        return instructor_sum

    if instructor_sum == instructor_attendee:
        return instructor_sum
    print(f'conflicting instructors: {instructor_sum} : {instructor_attendee}')
    return None


def virtual_or_in_person(event: Event, instructor: str) -> ClassLocation | None:
    if 'in person' in event.summary.lower() or 'hybrid' in event.summary.lower() or "in-person" in event.summary.lower():
        return ClassLocation.InPerson
    if "In House" == event.summary[:8]:
        return ClassLocation.Virtual

    if 'virtual' in event.summary.lower() or instructor == "Gorirossi":
        return ClassLocation.Virtual
    if event.description is None:
        return ClassLocation.Virtual

    if len(event.description) > 100:
        return ClassLocation.InPerson
    # print(f'description: [{len(event.description)}] [{type(event.description)}]')
    return ClassLocation.Virtual
    # print(f'Error: No location (in person or virtual)')
    # return None
