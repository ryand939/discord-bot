from datetime import datetime, timedelta
import json
from random import randrange


class Task():

    def __init__(self):
        self.status = None 
        self.description = None 
        self.endTime = None 
        self.startTime = None 
        self.taskJSON = json.load(open(f"./resources/priv9/tasks.json"))
        self.start_new_task()
        
    def start_new_task(self):
        self.startTime = datetime.now()
        self.status, self.description = self.get_specific_task()
        self.endTime = datetime.now() + self.get_time_delta()

    def get_specific_task(self):
        hour = self.startTime.hour

        if hour < 2:                           # 0 - 1
            return self.get_task("late_task")
        elif hour < 10:                        # 2 - 9
            return self.get_task("sleep_task")
        elif hour < 14:                        # 10 - 13
            return self.get_task("morning_task")
        elif hour < 16:                        # 14 - 15
            return self.get_task("work_task")
        elif hour < 18:                        # 16 - 17
            return self.get_task("break_task")
        elif hour < 20:                        # 18 - 19
            return self.get_task("dinner_task")
        elif hour < 22:                        # 20 - 21
            return self.get_task("work_task")
        elif hour <= 23:                       # 22 - 23
            return self.get_task("break_task")

    def get_time_delta(self):
        targetHour = self.startTime.hour
        # get target time = next one of the following hours:
        # these are the hours i want the dev to have a new status
        checkPoints = [0, 2, 4, 6, 8, 10, 14, 16, 18, 20, 22]
        
        if checkPoints.count(targetHour) > 0:
            index = checkPoints.index(targetHour)
            if (index + 1) == len(checkPoints):
                targetHour = checkPoints[0]
            else:
                targetHour = checkPoints[index + 1]
        # while the number is not a checkpoint num, keep adding to it until it hits a checkpoint
        while(checkPoints.count(targetHour) == 0):
            targetHour += 1
            if targetHour == 24:
                targetHour = 0

        # if the target hour is 0, the target is the beginning of the next day
        if targetHour == 0:
            # add a day to the current time, then reset it's hour/min/sec with .min
            tempDate = self.startTime + datetime.timedelta(days=1)
            targetDelta = datetime.combine(tempDate, datetime.time.min) - self.startTime
        else:
            # replace the current time with the target hour, then get the delta
            tempDate = self.startTime.replace(hour=targetHour, minute=0)
            targetDelta = tempDate - self.startTime

        return targetDelta


    # returns all information regarding the current task
    # status, description, time until expiry
    def get_current_task(self):
        self.refresh()
        return self.status, self.description, ((self.endTime - datetime.now()).total_seconds() // 60)


    # get a new task if the current task expired
    def refresh(self):
        if self.endTime < datetime.now():
            self.start_new_task()

  
    def get_task(self, type_task):
        index = randrange(len(self.taskJSON[type_task][0]))
        rtnStatus = list(self.taskJSON[type_task][0])[index]
        rtnDesc = self.taskJSON[type_task][0][rtnStatus]
        return rtnStatus, rtnDesc
