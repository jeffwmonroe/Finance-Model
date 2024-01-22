import datetime
import os.path
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import config

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def trimmed_ds(date_str: str) -> datetime.datetime:
    tloc = date_str.find("T")
    if tloc > -1:
        date_str = date_str[:tloc]
    date_str = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    return date_str


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(config['token']):
        creds = Credentials.from_authorized_user_file(config['token'], SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config['credentials'], SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(config['token'], "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        # now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat() + "Z"
        print(f'now = {now}')
        print(f'date type = {type(now)}')
        print("Getting the upcoming 10 events")
        jan = datetime.datetime(2023, 1, 1, 0, 0, 0).isoformat() + "Z"
        dec = datetime.datetime(2023, 12, 31, 11, 59, 59).isoformat() + "Z"
        print(f'jan = {jan}')
        print(f'dec = {dec}')
        print('-'*15)
        print(service.events())
        print('-'*15)
        events_result = (
            service.events()
            .list(
                calendarId="haztraintraining@gmail.com",
                # calendarId="monroe.jeffw@gmail.com",
                timeMin=jan,
                timeMax=dec,
                # maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        print(f'Total amount of classes: {len(events)}')
        if not events:
            print("No upcoming events found.")
            return

        instructor_list = ["Czysz", "Reising", "Wood", "Gorirossi", "McCrea", "Della-Volle", "Spheeris"]
        inst_df = pd.DataFrame({"Virtual": [0]*len(instructor_list),
                                "In Person": [0]*len(instructor_list),
                                "Travel": [0]*len(instructor_list),
                                "Holiday": [9]*len(instructor_list),
                                "PTO": [0,
                                        6.66 * 24 / 8,
                                        6.66 * 24 / 8,
                                        6.66 * 24 / 8,
                                        6.66 * 24 / 8,
                                        0,
                                        0,
                                        ],
                                "Sick": [10]*len(instructor_list),
                                "Pay": [0,
                                        80000,
                                        124800,
                                        75504,
                                        92400,
                                        0,
                                        0,
                                        ],
                                },
                               index=instructor_list)
        pruned_events = []
        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            start = trimmed_ds(start)

            end = event["end"].get("dateTime", event["end"].get("date"))
            end = trimmed_ds(end)
            delta = end-start
            summary = event["summary"]
            if (summary[:3] == 'DNB' or
                summary[-3:] == 'DNB' or
                summary[:2] == 'QM' or
                "cancelled" in summary.lower() or
                summary[:9].lower() == 'no travel' or
                summary[:12].lower() == 'virtual only' or
                summary[-3:].lower() == "off"):
                pruned_events.append(event)
                continue
            instructor = None
            for inst in instructor_list:
                if inst.lower() in summary.lower():
                    instructor = inst
                    break
            if instructor is None:
                # print(f'no instructor {start.strftime("%Y-%m-%d")} - {end.strftime("%Y-%m-%d")} ({event["summary"]}) : [{instructor}]{delta.days} days long')
                pass
                continue
            class_location = None
            if 'in person' in summary.lower() or 'hybrid' in summary.lower() or "in-person" in summary.lower():
                # print('in person')
                class_location = "In Person"
                inst_df.loc[instructor, "In Person"] = inst_df.loc[instructor, "In Person"] + delta.days
                inst_df.loc[instructor, "Travel"] = inst_df.loc[instructor, "Travel"] + 2
                continue
            if 'virtual' in summary.lower() or instructor == "Gorirossi":
                # print('virtual')
                class_location = "Virtual"
                inst_df.loc[instructor, "Virtual"] = inst_df.loc[instructor, "Virtual"] + delta.days
                continue
            # print(f'{start.strftime("%Y-%m-%d")} - {end.strftime("%Y-%m-%d")} ({event["summary"]}) : [{instructor}]{delta.days} days long')
            inst_df.loc[instructor, "In Person"] = inst_df.loc[instructor, "In Person"] + delta.days
            inst_df.loc[instructor, "Travel"] = inst_df.loc[instructor, "Travel"] + 2
            # Assume in person
        # inst_df["Total"] = inst_df.loc[["Virtual", "In Person", "Travel"]].sum(axis=1)
        inst_df["Total"] = inst_df.loc[:, ["Virtual", "In Person", "Travel", "Holiday", "PTO", "Sick"]].sum(axis=1)
        inst_df["Perc"] = inst_df.loc[:, "Total"] / 2080 * 8
        print(inst_df)
    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == "__main__":
    main()
