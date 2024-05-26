import functools
from typing import Callable, ParamSpec

from typing_extensions import TypeVar

_P = ParamSpec("_P")
_R = TypeVar("_R")


def typed_partial(f: Callable[_P, _R]) -> Callable[_P, Callable[_P, _R]]:
    """Given a function, returns a function that takes arguments for that function and
    returns a function that calls the original function with the partial arguments and
    whatever's passed into it.

    Basically, this is a more strongly typed version of `functools.partial`.
    """

    @functools.wraps(f)
    def builder_builder(*partial_args: _P.args, **partial_kwargs: _P.kwargs):
        @functools.wraps(f)
        def builder(*args: _P.args, **kwargs: _P.kwargs):
            return f(*partial_args, *args, **partial_kwargs, **kwargs)

        return builder

    return builder_builder
