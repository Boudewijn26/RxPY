from typing import Any, List, Optional, TypeVar

from rx.core import Observable, abc
from rx.core.notification import Notification
from rx.disposable import Disposable
from rx.scheduler import VirtualTimeScheduler

from .recorded import Recorded
from .subscription import Subscription

_T = TypeVar("_T")


class HotObservable(Observable[_T]):
    def __init__(
        self, scheduler: VirtualTimeScheduler, messages: List[Recorded[_T]]
    ) -> None:
        super().__init__()

        self.scheduler: VirtualTimeScheduler = scheduler
        self.messages = messages
        self.subscriptions: List[Subscription] = []
        self.observers: List[abc.ObserverBase[_T]] = []

        observable = self

        def get_action(notification: Notification[_T]):
            def action(scheduler: abc.SchedulerBase, state: Any):
                for observer in observable.observers[:]:
                    notification.accept(observer)
                return Disposable()

            return action

        for message in self.messages:
            notification = message.value

            # Warning: Don't make closures within a loop
            action = get_action(notification)
            scheduler.schedule_absolute(message.time, action)

    def _subscribe_core(
        self,
        observer: Optional[abc.ObserverBase[_T]] = None,
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        if observer:
            self.observers.append(observer)
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1

        def dispose_action():
            if observer:
                self.observers.remove(observer)
            start = self.subscriptions[index].subscribe
            end = self.scheduler.clock
            self.subscriptions[index] = Subscription(start, end)

        return Disposable(dispose_action)
