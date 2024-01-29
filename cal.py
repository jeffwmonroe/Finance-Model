import datetime
import os.path
import pandas as pd

import haztrain_calendar as hc
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence, DAILY, SU, SA

import haztrain_calendar as hc


def main():
    calendar = GoogleCalendar('haztraintraining@gmail.com', credentials_path='./.credentials/credentials.json')

    jan = datetime.datetime(2023, 1, 1, 0, 0, 0)
    dec = datetime.datetime(2023, 12, 31, 11, 59, 59)

    inst_dict, inst_df = hc.get_instructor_info()
    events = list(calendar.get_events(jan, dec, order_by="startTime", single_events=True))

    for event in events:
        start = event.start
        end = event.end
        delta = end - start
        summary = event.summary
        if hc.event_type(summary) != hc.EventType.Training:
            continue
        instructor = hc.get_instructor(event, inst_dict)
        if instructor is None:
            continue
        location = hc.virtual_or_in_person(event, instructor)
        if location is None:
            # print(f'{start} - {end} {summary} [{delta}]')
            print(f'{start} - {end} {summary} [{delta}] : [{event.description}]')
            # break
        if location == hc.ClassLocation.InPerson:
            inst_df.loc[instructor, "In Person"] = inst_df.loc[instructor, "In Person"] + delta.days
            inst_df.loc[instructor, "Travel"] = inst_df.loc[instructor, "Travel"] + 2
        elif location == hc.ClassLocation.Virtual:
            inst_df.loc[instructor, "Virtual"] = inst_df.loc[instructor, "Virtual"] + delta.days
        print(f'{start} - {end} {summary} [{delta}] : [{event.event_id}]')

    inst_df["Total"] = inst_df.loc[:, ["Virtual", "In Person", "Travel", "Holiday", "PTO", "Sick"]].sum(axis=1)
    inst_df["Perc"] = inst_df.loc[:, "Total"] / 2080 * 8
    print(inst_df)
if __name__ == "__main__":
    main()
