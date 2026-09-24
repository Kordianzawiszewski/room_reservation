import google_calendar
import datetime

service = google_calendar.get_calendar_service()

start_time = datetime.datetime.fromisoformat("2026-09-20T12:00:00+02:00")
end_time = datetime.datetime.fromisoformat("2026-09-20T13:00:00+02:00")

created_event = google_calendar.create_calendar_event(service, "Test room reservation", start_time, end_time)

print(created_event["htmlLink"])