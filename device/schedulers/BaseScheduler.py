# coding=utf-8
import sys
import os
import json
import datetime
import time
import pytz
import _strptime
from queue import Queue

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from util import read_from_file
from config import TIME_ZONE, TIME_ZONE_STATUS

# schedule file with two-dimension list from 0 - 6 matching with Mon - Sun
class BaseScheduler:

    def __init__(self, schedule_file, queue, thread_event):
        self.queue = queue if queue else Queue(maxsize=0)
        self.schedules = []
        self.schedule_file = schedule_file
        self.thread_event = thread_event

    """
        light schedule example
        [
            [
                {
                    'schedule_hour': '00:00:00',
                    'sig': 'on'
                },
                {
                    'schedule_hour': '06:00:00',
                    'sig': 'off'
                },
                {
                    'schedule_hour': '10:00:00',
                    'sig': 'boost'
                }
            ],
        ]
        pump schedule example
        [
            [
                {
                    'schedule_hour': '00:00:00',
                    'sig': 900
                },
                {
                    'schedule_hour': '06:00:00',
                    'sig': 900
                }
            ],
        ]
    """
    def get_closet_schedule(self):
        self.reset_tz() 
        date_today, day_of_week, now = self.today()
        print("day of week", day_of_week)
        print("date today", date_today)
        schedule_index = 0
        diff = 24 * 60 * 60
        next_awaken_time = self.str_to_timestamp('{} {}'.format(date_today, '23:59:59'), "%Y-%m-%d %H:%M:%S") + 1
        
        if self.schedules[day_of_week]:
            for schedule in self.schedules[day_of_week]:
                schedule_time = self.str_to_timestamp('{} {}'.format(date_today, schedule.get('schedule_hour')), "%Y-%m-%d %H:%M:%S")
                if abs(diff) >= abs(schedule_time - now):
                    diff = schedule_time - now
                    schedule_index = self.schedules[day_of_week].index(schedule)
                    print('diff', diff, schedule_index)
            
            print('closet_index', schedule_index, len(self.schedules[day_of_week]))
            # if diff < 5 which means it suppose to start now
            if abs(diff) < 5:
                # if it's not the last schedule, then awake at next schedule during the day
                # otherwise awake at the 00:00:01 next morning
                if schedule_index < (len(self.schedules[day_of_week]) - 1):
                    next_awaken_time = self.str_to_timestamp('{} {}'.format(date_today, self.schedules[day_of_week][schedule_index + 1].get('schedule_hour')), "%Y-%m-%d %H:%M:%S")
                return self.schedules[day_of_week][schedule_index], (next_awaken_time - now)
            
            # if not yet start
            else:
                # diff > 0 means it hasn't reach the nearest schedule
                if diff > 0:
                    next_awaken_time = self.str_to_timestamp('{} {}'.format(date_today, self.schedules[day_of_week][schedule_index].get('schedule_hour')), "%Y-%m-%d %H:%M:%S")
                # diff < 0  means it passed the nearest schedule
                elif diff < 0 and schedule_index < (len(self.schedules[day_of_week]) - 1):
                    next_awaken_time = self.str_to_timestamp('{} {}'.format(date_today, self.schedules[day_of_week][schedule_index + 1].get('schedule_hour')), "%Y-%m-%d %H:%M:%S")
                return None, (next_awaken_time - now)

        else:
            return None, (next_awaken_time - now)
            
    def run(self):
        while True:
            if self.thread_event.is_set():
                self.thread_event.clear()
            self.load_schedules(self.schedule_file)
            schedule, time_to_sleep = self.get_closet_schedule()
            print(schedule)
            print('next sleeping duration: {}'.format(time_to_sleep))
            if schedule:
                print('put in queue')
                sig = schedule.get('sig')
                self.queue.put(sig)
            if self.thread_event:
                self.thread_event.wait(time_to_sleep)
            else:
                time.sleep(time_to_sleep)

    def load_schedules(self, path):
        with open(path, 'r') as fp:
            self.schedules = json.load(fp)
        
    def reset(self):
        self.schedules = []
        self.load_schedules()

    def str_to_timestamp(self, ts, format):
        ts = datetime.datetime.strptime(ts, format)
        rts = self.tz.localize(ts)
        return int(time.mktime(rts.timetuple()))

    def today(self):
        time_zone = read_from_file(os.path.dirname(TIME_ZONE_STATUS), os.path.basename(TIME_ZONE_STATUS)) or TIME_ZONE
        now = datetime.datetime.now(self.tz)
        return datetime.datetime.strftime(now, '%Y-%m-%d'), now.weekday(), time.mktime(now.timetuple())

    def reset_tz(self):
        time_zone = read_from_file(os.path.dirname(TIME_ZONE_STATUS), os.path.basename(TIME_ZONE_STATUS)) or TIME_ZONE
        try:
            self.tz = pytz.timezone(time_zone)
        except Exception as e:
            time_zone = TIME_ZONE
            self.tz = pytz.timezone(time_zone)
        finally:
            print('timezone reset: {}'.format(time_zone))

if __name__ == "__main__":
    light_q = Queue(maxsize=0)
    light_scheduler = BaseScheduler('../schedules/light_schedule.json', light_q)
    light_scheduler.run()