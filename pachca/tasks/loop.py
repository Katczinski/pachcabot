from typing import (
    Any,
    Callable,
    Optional,
)
import asyncio
import threading
import datetime

class Loop:
    _task:asyncio.Task
    _func:Callable
    _loop:asyncio.AbstractEventLoop
    _seconds:float
    _hours: float
    _minutes: float
    _time: datetime.time
    _count: Optional[int]
    _stopped:bool
    _sleep:float

    def __init__(
            self,
            func:Callable,
            seconds: float,
            hours: float,
            minutes: float,
            time: datetime.time,
            count: Optional[int],
            start:bool
            ) -> None:
        self._func = func
        time = None # Not supported yet
        self.calculate_interval(seconds, minutes, hours, time)

        self._count = count
        self._stopped = True
        self._loop = asyncio.get_event_loop()
        self.daemon_run()
        if start:
            self.start()
        
    def calculate_interval(
        self,
        seconds: float = 0,
        minutes: float = 0,
        hours: float = 0,
        time: datetime.time = None
        ) -> None:
        if time is None:
            seconds = seconds or 0
            minutes = minutes or 0
            hours = hours or 0
            sleep = seconds + (minutes * 60.0) + (hours * 3600.0)
            if sleep < 0:
                raise ValueError('Total number of seconds cannot be less than zero.')

            self._sleep = sleep
            self._seconds = float(seconds)
            self._hours = float(hours)
            self._minutes = float(minutes)
            self._time = None
        else:
            if any((seconds, minutes, hours)):
                raise TypeError('Cannot mix explicit time with relative time')

    def _is_relative_time(self) -> bool:
        return self._time is None

    def _is_explicit_time(self) -> bool:
        return self._time is not None

    async def loop_wrapper(self):
        print("loop started")
        while not self._stopped:
            try:
                await self._func()
                print("sleeping", str(datetime.timedelta(0, self._sleep)))
                await asyncio.sleep(self._sleep)
            except Exception as e:
                print(e)
                self.stop()          
        print("loop stopped")

    def stop(self) -> bool:
        if not self._stopped:
            self._stopped = True
            return True
        return False

    def start(self) -> bool:
        if self._stopped:
            self._stopped = False
            asyncio.run_coroutine_threadsafe(self.loop_wrapper(), self._loop)
            return True
        return False

    def daemon_run(self):
        thr = threading.Thread(target=self._loop.run_forever, daemon=True)
        print("starting daemon")
        thr.start()


def loop(
    seconds: float = None,
    minutes: float = None,
    hours: float = None,
    time: datetime.time = None,
    count: Optional[int] = None,
    start:bool = False
    ) -> Callable:
    def decorator(func) -> Loop:
        return Loop(
            func,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            time=time,
            count=count,
            start=start
        )
    return decorator