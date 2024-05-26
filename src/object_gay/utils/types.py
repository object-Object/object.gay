import functools
from typing import Annotated, Any, Callable, ParamSpec

from pydantic import AnyHttpUrl, BeforeValidator, TypeAdapter
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


def _url_validator(model_type: Any):
    return TypeAdapter(model_type).validate_python


AnyHttpUrlStr = Annotated[
    str,
    BeforeValidator(lambda v: str(v).rstrip("/")),
    BeforeValidator(_url_validator(AnyHttpUrl)),
]
