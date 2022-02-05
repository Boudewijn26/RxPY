from typing import Any, Callable, List, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, pipe

_T = TypeVar("_T")


def buffer(
    boundaries: Observable[Any],
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    return pipe(
        ops.window(boundaries), ops.flat_map(pipe(ops.to_iterable(), ops.map(list)))
    )


def _buffer_when(
    closing_mapper: Callable[[], Observable]
) -> Callable[[Observable], Observable]:
    return pipe(
        ops.window_when(closing_mapper),
        ops.flat_map(pipe(ops.to_iterable(), ops.map(list))),
    )


def _buffer_toggle(
    openings: Observable, closing_mapper: Callable[[Any], Observable]
) -> Callable[[Observable], Observable]:
    return pipe(
        ops.window_toggle(openings, closing_mapper),
        ops.flat_map(pipe(ops.to_iterable(), ops.map(list))),
    )


def buffer_with_count(
    count: int, skip: Optional[int] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Projects each element of an observable sequence into zero or more
    buffers which are produced based on element count information.

    Examples:
        >>> res = buffer_with_count(10)(xs)
        >>> res = buffer_with_count(10, 1)(xs)

    Args:
        count: Length of each buffer.
        skip: [Optional] Number of elements to skip between
            creation of consecutive buffers. If not provided, defaults to
            the count.

    Returns:
        A function that takes an observable source and returns an
        observable sequence of buffers.
    """

    def buffer_with_count(source: Observable[_T]) -> Observable[List[_T]]:
        nonlocal skip

        if skip is None:
            skip = count

        def mapper(value: _T) -> List[_T]:
            return value.pipe(ops.to_iterable(), ops.map(list))

        def predicate(value: List[_T]) -> bool:
            return len(value) > 0

        return source.pipe(
            ops.window_with_count(count, skip),
            ops.flat_map(mapper),
            ops.filter(predicate),
        )

    return buffer_with_count


__all__ = ["buffer", "buffer_with_count"]
