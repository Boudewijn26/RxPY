import itertools
from asyncio import Future
from typing import Callable, Union, TypeVar

import rx
from rx.core import Observable
from rx.core.typing import Predicate
from rx.internal.utils import infinite

_T = TypeVar("_T")


def while_do(condition: Predicate[_T]) -> Callable[[Observable[_T]], Observable[_T]]:
    def while_do(source: Union[Observable[_T], "Future[_T]"]) -> Observable[_T]:
        """Repeats source as long as condition holds emulating a while
        loop.

        Args:
            source: The observable sequence that will be run if the
                condition function returns true.

        Returns:
            An observable sequence which is repeated as long as the
            condition holds.
        """
        if isinstance(source, Future):
            obs = rx.from_future(source)
        else:
            obs = source
        it = itertools.takewhile(condition, (obs for _ in infinite()))
        return rx.concat_with_iterable(it)

    return while_do


__all__ = ["while_do"]
