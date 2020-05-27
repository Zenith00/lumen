from __future__ import annotations

import abc
import collections
import typing as ty
import asyncio
import aenum

if ty.TYPE_CHECKING:
    pass


class AutoRepr:
    @staticmethod
    def repr(obj):
        items = []
        for prop, value in obj.__dict__.items():
            try:
                item = "%s = %r" % (prop, value)
                assert len(item) < 100
            except:
                item = "%s: <%s>" % (prop, value.__class__.__name__)
            items.append(item)

        return "%s(%s)" % (obj.__class__.__name__, ', '.join(items))

    def __init__(self, cls):
        cls.__repr__ = AutoRepr.repr
        self.cls = cls

    def __call__(self, *args, **kwargs):
        return self.cls(*args, **kwargs)


@AutoRepr
class Event:
    def __init__(self, evats: ty.Set[EventAttribute], kwargs: dict):
        self.evats = evats
        self.kwargs = kwargs


class EventAdapter(abc.ABC):
    def __init__(self, source):
        self.source = source

    def register_event(self) -> None:
        pass

    def eventize_deco_factory(self, driver: Driver, evats: ty.Tuple[EventAttribute]) -> ty.Callable[
        [ty.Tuple[EventAttribute]],
        ty.Callable[
            [ty.Callable],
            ty.Callable[
                ...,
                ty.Awaitable[ty.Dict]
            ]
        ]
    ]:
        pass

    async def register(self, driver: Driver) -> None:
        pass


class EventAttribute(aenum.Flag):
    ...


class EventListener:
    def __init__(self, func: ty.Callable[[Event], ty.Any], filter_func: ty.Callable[[Event], bool]):
        self.func = func
        self.filter_func = filter_func

    async def submit_run(self, event: Event) -> None:
        if self.filter_func(event):
            await self.func(event)

class EventRefinery:
    def __init__(self,  filter_func: ty.Callable[[Event], bool], refinery:  ty.Callable[[Event], ty.Tuple[Event]]):
        self.filter_func = filter_func
        self.refine = refinery

    def submit(self, event: Event, event_queue: ty.Deque[Event]):
        if self.filter_func(event):
            event_queue.extend(self.refine(event))




class Driver:
    def __init__(self):
        self.event_filters: ty.List[EventListener] = []
        self.event_refineries = []
        self.events = collections.deque()

    async def submit(self, event: Event) -> None:
        self.events.append(event)

        while self.events:
            ev = self.events.popleft()
            [refinery.submit(ev) for refinery in self.event_refineries]

            await asyncio.gather(*[ev_filter.submit_run(event) for ev_filter in self.event_filters])

    def register_adapter(self, adapter: EventAdapter):
        adapter.register(self)

    def register_refinery(self, refinery: EventRefinery):
        self.event_refineries.append(refinery)

    def register_listener_deco_factory(self, filter_func: ty.Callable[[Event], bool]):
        def register_listener_deco(func):
            self.event_filters.append(EventListener(func, filter_func))

        return register_listener_deco
