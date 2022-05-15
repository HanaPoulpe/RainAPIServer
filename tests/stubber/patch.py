"""Base patch for unittest"""
import collections
import types
import typing


class MockCallable:
    """
    Create a fake callable

    >>> MockCallable()  # Creates a callable the keeps track of calls, returns nothing
    >>> MockCallable(return_value="return this")  # Always returns the same value
    >>> MockCallable(return_value_list=["return_1", "return_2"])
    >>> # Returns the values from first to last,
    >>> # when last is reached: keeps returning it
    >>> MockCallable(side_effect=ValueError()) # Raises a value error at each call
    >>> MockCallable(side_effect_list=[ValueError(), None])  # Raises a ValueError at the first call
    >>> # then return the return_value
    """

    calls_type = collections.namedtuple("CallsType", ["args", "kwargs", "return_value",
                                                      "raise_error"])

    def __init__(
            self, *,
            return_value: typing.Any | None = None,
            return_value_list: list[typing.Any | None] | None = None,
            side_effect: Exception | None = None,
            side_effect_list: list[Exception | None] | None = None
    ):
        if return_value and return_value_list:
            raise ValueError("return_value and return_value_list can't both be used together.")
        if side_effect and side_effect_list:
            raise ValueError("side_effect and side_effect_list can't both be used together.")

        if return_value_list:
            self.__return_values = return_value_list
        else:
            self.__return_values = [return_value]

        if side_effect_list:
            self.__side_effects = side_effect_list
        else:
            self.__side_effects = [side_effect]

        self.__return_iter = iter(self.__return_values)
        self.__current_return = next(self.__return_iter)
        self.__side_effect_iter = iter(self.__side_effects)
        self.__current_side_effect = next(self.__side_effect_iter)

        self.__calls: list[MockCallable.calls_type] = []

    def __call__(self, *args, **kwargs):
        self.__current_side_effect = next(self.__side_effect_iter, self.__current_side_effect)
        if self.__current_side_effect:
            raise self.__current_side_effect

        self.__current_return = next(self.__return_iter, self.__current_return)
        return self.__current_return

    def _add_call(self, call_spec: "MockCallable.calls_type"):
        """Add a call the call list"""
        self.__calls.append(call_spec)

    @property
    def calls(self) -> list["MockCallable.calls_type"]:
        return self.__calls


class CallableTracker(MockCallable):
    """
    Replaces a callable with an object that keeps trace of the calls parameters and returns

    >>> import os
    >>>
    >>> CallableTracker("getenv", os)
    >>> os.getenv("MY_ENV")
    >>> print(os.getenv.calls)  # type: ignore
    """

    def __init__(self, callable_name: str, module: types.ModuleType):
        super().__init__()
        self.__fnc = getattr(module, callable_name)
        self.__module = module
        self.__callable_name = callable_name
        setattr(module, callable_name, self)

    def __call__(self, *args, **kwargs):
        try:
            return_value = self.__fnc(*args, **kwargs)
        except Exception as err:
            self._add_call(self.calls_type(args, kwargs, None, err))
            raise err
        self._add_call(self.calls_type(args, kwargs, return_value, None))

    def tear_down(self):
        setattr(self.__module, self.__callable_name, self.__fnc)
