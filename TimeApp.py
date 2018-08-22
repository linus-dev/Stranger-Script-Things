import win32evtlog
import datetime

USERNAME = 'LGU76C'
PUNCHCARD = dict()

def SetupDate(time_dict, time):
  year = time.year
  month = time.month
  day = time.day
  if (year not in time_dict):
    time_dict[year] = dict()
  if (month not in time_dict[year]):
    time_dict[year][month] = dict()
  if (day not in time_dict[year][month]):
    time_dict[year][month][day] = dict()
  return time_dict

def TimeDelta(a, b):
  format = '%m/%d/%y %H:%M:%S'
  a = datetime.datetime.strptime(str(a), format)
  b = datetime.datetime.strptime(str(b), format)
  return datetime.timedelta(seconds=((b - a).total_seconds()))

def GatherLogs():
  server = 'localhost' # name of the target computer to get event logs
  logtype = 'Security'
  hand = win32evtlog.OpenEventLog(server, logtype)
  flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
  total = win32evtlog.GetNumberOfEventLogRecords(hand)
  events = win32evtlog.ReadEventLog(hand, flags, 0)
  while events:
    if events:
      for event in events:
        if (event.EventID == 4648): # LOGON
          data = event.StringInserts
          if (data):
            if(USERNAME.lower() in data or USERNAME.upper() in data):
              current = event.TimeGenerated
              year = current.year
              month = current.month
              day = current.day
              SetupDate(PUNCHCARD, event.TimeGenerated)
              PUNCHCARD[year][month][day]['work_start'] = current
        # Max logoff date
        if (event.EventID == 4634 or event.EventID == 4647): # LOGOFF
          data = event.StringInserts
          if (data):
            if(USERNAME.lower() in data or USERNAME.upper() in data):
              current = event.TimeGenerated
              year = current.year
              month = current.month
              day = current.day
              SetupDate(PUNCHCARD, event.TimeGenerated)
              if (not PUNCHCARD[year][month][day]):
                PUNCHCARD[year][month][day]['work_end'] = current

    events = win32evtlog.ReadEventLog(hand, flags, 0)
  
  # Print work period.
  print('--HOURS WORKED--')
  for year in PUNCHCARD:
    for month in PUNCHCARD[year]:
      for day in PUNCHCARD[year][month]:
        start = PUNCHCARD[year][month][day]['work_start']
        end = PUNCHCARD[year][month][day]['work_end']
        if (start.hour > 9):
          continue
        delta = TimeDelta(start, end)
        print('{}/{}/{} - {} - {} - {}'.format(str(day), str(month), str(year), str(delta), start, end))
  
if __name__ == '__main__':
  GatherLogs()
