# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Metaclasses used in various explicit classes in PyFluent."""

from abc import ABC, abstractmethod
import inspect
from collections.abc import Callable, Iterator, MutableMapping, Sequence
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    Generic,
    Never,
    Protocol,
    Self,
    Unpack,
    cast,
    overload,
    override,
)

from ansys.fluent.core.exceptions import DisallowedValuesError
from ansys.fluent.core.session_solver import Solver
from typing_extensions import (
    NotRequired,
    ParamSpec,
    TypedDict,
    TypeVar,
    get_args,
    get_original_bases,
)

from ansys.fluent.interface.post_objects.post_helper import PostAPIHelper
from ansys.fluent.interface.post_objects.post_object_definitions import (
    BasePostObjectDefn,
    ContourDefn,
    Defns,
    MonitorDefn,
    VectorDefn,
)

if TYPE_CHECKING:
    from ansys.fluent.core.services.field_data import LiveFieldData
    from ansys.fluent.core.streaming_services.monitor_streaming import MonitorsManager

    from ansys.fluent.interface.post_objects.post_object_definitions import (
        GraphicsDefn,
        PlotDefn,
    )
    from ansys.fluent.interface.post_objects.post_objects_container import Container

# pylint: disable=unused-private-member
# pylint: disable=bad-mcs-classmethod-argument

_SelfT = TypeVar("_SelfT", covariant=True)
_T_co = TypeVar("_T_co", covariant=True)


class HasAttributes(Protocol):
    # attributes: NotRequired[set[str]]  # technically this but this is just object
    attributes: set[str]


class Attribute(Generic[_SelfT, _T_co]):
    """Attributes."""

    VALID_NAMES = (
        "range",
        "allowed_values",
        "display_name_allowed_values",
        "help_str",
        "is_read_only",
        "is_active",
        "on_create",
        "on_change",
        "show_as_separate_object",
        "display_text",
        "layout",
        "previous",
        "next",
        "include",
        "exclude",
        "sort_by",
        "style",
        "icon",
        "show_text",
        "widget",
        "dir_info",
        "extensions",
    )

    def __init__(self, function: Callable[[_SelfT], _T_co], /):
        self.function = function
        self.__doc__: str | None = getattr(function, "__doc__", None)
        self.name: str

    def __set_name__(self, owner: HasAttributes, name: str):
        if name not in self.VALID_NAMES:
            raise DisallowedValuesError("attribute", name, self.VALID_NAMES)
        self.name = name
        if not hasattr(owner, "attributes"):
            owner.attributes = set[str]()
        assert isinstance(owner.attributes, set)
        owner.attributes.add(name)

    def __set__(
        self,
        instance: _SelfT,    # pyright: ignore[reportGeneralTypeIssues]
        value: _T_co,  # pyright: ignore[reportGeneralTypeIssues]
    ) -> Never:
        raise AttributeError("Attributes are read only.")

    @overload
    def __get__(self, instance: None, _) -> Self: ...

    @overload
    def __get__(
        self,
        instance: _SelfT,    # pyright: ignore[reportGeneralTypeIssues]
        _,
    ) -> _T_co: ...

    def __get__(self, instance: _SelfT | None, _) -> _T_co | Self:
        if instance is None:
            return self
        return self.function(instance)


P = ParamSpec("P")


class Command(Generic[_SelfT, P]):
    """Executes command."""

    def __init__(self, method: Callable[Concatenate[_SelfT, P], None]):
        self.arguments_attrs = {}
        self.owner: type

        cmd_args = inspect.signature(method).parameters
        for arg_name in cmd_args:
            if arg_name != "self":
                self.arguments_attrs[arg_name] = {}

        def _init(_self: _SelfT, obj):
            _self.obj = obj

        def _execute(_self: _SelfT, *args: Any, **kwargs: Any):
            for arg, attr_data in self.arguments_attrs.items():
                arg_value = None
                if arg in kwargs:
                    arg_value = kwargs[arg]
                else:
                    index = list(self.arguments_attrs.keys()).index(arg)
                    if len(args) > index:
                        arg_value = args[index]
                if arg_value is not None:
                    for attr, attr_value in attr_data.items():
                        if attr == "allowed_values":
                            allowed_values = attr_value(_self.obj)
                            if isinstance(arg_value, list):
                                if not all(
                                    elem in allowed_values for elem in arg_value
                                ):
                                    raise DisallowedValuesError(
                                        arg, arg_value, allowed_values
                                    )
                            else:
                                if arg_value not in allowed_values:
                                    raise DisallowedValuesError(
                                        arg, arg_value, allowed_values
                                    )

                        elif attr == "range":
                            if not isinstance(arg_value, (int, float)):
                                raise RuntimeError(
                                    f"{arg} value {arg_value} is not number."
                                )

                            minimum, maximum = attr_value(_self.obj)
                            if arg_value < minimum or arg_value > maximum:
                                raise DisallowedValuesError(
                                    arg, arg_value, allowed_values
                                )
            return method(_self.obj, *args, **kwargs)

        self.command_cls = type(
            "command",
            (),
            {
                "__init__": _init,
                "__call__": _execute,
                "argument_attribute": (
                    lambda _self, argument_name, attr_name: self.arguments_attrs[
                        argument_name
                    ][attr_name](_self.obj)
                ),
                "arguments": lambda _self: list(self.arguments_attrs.keys()),
            },
        )

    def __set_name__(self, owner: type, name: str) -> None:
        self.owner = owner
        if not hasattr(owner, "commands"):
            owner.commands = {}
        owner.commands[name] = {}

    def __get__(self, instance: _SelfT, _):  # pyright: ignore[reportGeneralTypeIssues]
        return self.command_cls(instance)


TT = TypeVar("TT", bound=type)
T = TypeVar("T")
T2 = TypeVar("T2")

AccessorT = TypeVar("AccessorT", bound=BasePostObjectDefn)

ParentT = TypeVar("ParentT")

class PyLocalBase(Generic[ParentT]):
    """Local base."""

    def __init__(self, parent: ParentT, name: str = ""):
        self._parent = parent
        self._name = name

    def get_ancestors_by_type(
        self, instance: type[AccessorT], owner: "PyLocalBase[Any] | None" = None
    ) -> AccessorT:
        owner = self if owner is None else owner
        parent = None
        if hasattr(owner, "_parent"):
            if isinstance(owner._parent, instance):
                return owner._parent
            parent = self.get_ancestors_by_type(instance, owner._parent)
        assert parent is not None
        return parent

    def get_root(self, instance=None) -> Container:
        instance = self if instance is None else instance
        parent = instance
        if hasattr(instance, "_parent"):
            parent = self.get_root(instance._parent)
        return parent

    def get_session(self, instance) -> Solver:
        root = self.get_root(instance)
        return root.session

    def get_path(self) -> str:
        if hasattr(self, "_parent"):
            return self._parent.get_path() + "/" + self._name
        return self._name

    @property
    def root(self) -> Container:
        """Top-most parent object."""
        return self.get_root(self)

    @property
    def path(self) -> str:
        """Path to the current object."""
        return self.get_path()

    @property
    def session(self) -> "Solver":
        """Session associated with the current object."""
        return self.get_session(self)

    @property
    def field_data(self) -> "LiveFieldData":
        """Field data associated with the current object."""
        return self.session.fields.field_data

    @property
    def monitors(self) -> "MonitorsManager":
        """Monitors associated with the current object."""
        return self.session.monitors


class PyLocalProperty(PyLocalBase[ParentT], Generic[ParentT, T]):
    """Local property classes."""

    value: T  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self, parent: ParentT, api_helper: type[PostAPIHelper], name: str = ""):
        super().__init__(parent, name)
        self._api_helper = api_helper(self)
        self._on_change_cbs = []
        self.type: type[T] = get_args(get_original_bases(self.__class__)[0])[
            0
        ]  # T for the class
        reset_on_change = (
            hasattr(self, "_reset_on_change") and getattr(self, "_reset_on_change")()
        )

        try:
            on_change = self.on_change
        except AttributeError:
            pass
        else:
            self._register_on_change_cb(on_change)
        if reset_on_change:
            for obj in reset_on_change:

                def reset() -> None:
                    setattr(self, "_value", None)
                    for on_change_cb in self._on_change_cbs:
                        on_change_cb()

                obj._register_on_change_cb(reset)

    def __call__(self) -> T:
        rv = self.value

        try:
            allowed_values = self.allowed_values
        except AttributeError:
            return rv
        else:
            if len(allowed_values) > 0 and (
                rv is None or (not isinstance(rv, list) and rv not in allowed_values)
            ):
                self.set_state(allowed_values[0])
                rv = self.value

        return rv

    if TYPE_CHECKING:

        def __set__(self, instance: object, value: T) -> None: ...

    def set_state(self, value: T):
        self.value = value
        for on_change_cb in self._on_change_cbs:
            on_change_cb()

    def _register_on_change_cb(self, on_change_cb: Callable[[], None]):
        self._on_change_cbs.append(on_change_cb)

    @Attribute
    @overload
    def allowed_values(self: "PyLocalProperty[Any, Sequence[T2]]") -> Sequence[T2]: ...
    @Attribute
    @overload
    def allowed_values(self: "PyLocalProperty[Any, T2]") -> Sequence[T2]: ...
    @Attribute
    def allowed_values(self) -> Sequence[object]:
        """Get allowed values."""
        raise NotImplementedError("allowed_values not implemented.")


# class PyReferenceObject:
#     """Local object classes."""

#     def __init__(self, parent, path, location, session_id, name: str = ""):
#         self._parent = parent
#         self.type = "object"
#         self.parent = parent
#         self._path = path
#         self.location = location
#         self.session_id = session_id

#         def update(clss):
#             for name, cls in inspect.getmembers(clss, predicate=inspect.isclass):
#                 if issubclass(cls, (PyLocalProperty, PyLocalObject)):
#                     setattr(
#                         self,
#                         name,
#                         cls(self, lambda arg: None, name),
#                     )
#                 if issubclass(cls, PyLocalNamedObject):
#                     setattr(
#                         self,
#                         cls.PLURAL,
#                         PyLocalContainer(self, cls, lambda arg: None, cls.PLURAL),
#                     )
#             for base_class in clss.__bases__:
#                 update(base_class)

#         update(self.__class__)

#     def get_path(self):
#         return self._path

#     def reset(self, path: str, location: str, session_id: str) -> None:
#         self._path = path
#         self.location = location
#         self.session_id = session_id
#         if hasattr(self, "_object"):
#             delattr(self, "_object")





class PyLocalObject(PyLocalBase[ParentT]):
    """Local object classes."""

    def __init__(
        self, parent: ParentT, api_helper: type[PostAPIHelper], name: str = ""
    ):
        """Create the initialization method for 'PyLocalObjectMeta'."""
        super().__init__(parent, name)
        self._api_helper = api_helper(self)
        self._command_names = []
        self.type = "object"

        update(self.__class__)

    def _add_classes_to_instance(self, clss: type[PyLocalBase[object]], api_helper: type[PostAPIHelper]) -> None:
        for name, cls in inspect.getmembers(clss, predicate=inspect.isclass):
            if issubclass(cls, PyLocalCommand):
                self._command_names.append(name)

            if issubclass(cls, (PyLocalProperty, PyLocalObject, PyLocalCommand)):
                setattr(
                    self,
                    name,
                    cls(self, api_helper, name),
                )
            if issubclass(cls, PyLocalNamedObject):
                setattr(
                    self,
                    cls.PLURAL,
                    PyLocalContainer(self, cls, api_helper, cls.PLURAL),
                )
            # if issubclass(cls, PyReferenceObject):
            #     setattr(
            #         self,
            #         name,
            #         cls(self, cls.PATH, cls.LOCATION, cls.SESSION, name),
            #     )
        for base_class in clss.__bases__:
            update(base_class)

    def update(self, value: dict[str, Any]):
        """Update object."""
        properties = value
        sort_by = None
        if hasattr(self, "sort_by"):
            sort_by = self.sort_by
        elif hasattr(self, "include"):
            sort_by = self.include
        if sort_by:
            sorted_properties = {
                prop: properties[prop] for prop in sort_by if prop in properties
            }
            sorted_properties.update(
                {k: v for k, v in properties.items() if k not in sort_by}
            )
            properties.clear()
            properties.update(sorted_properties)
        for name, val in properties.items():
            obj = getattr(self, name)
            if isinstance(obj, PyLocalProperty):
                obj.set_state(val)
            else:
                # if isinstance(obj, PyReferenceObject):
                #     obj = obj.ref
                obj.update(val)

    def get_state(self, show_attributes: bool = False) -> dict[str, Any] | None:
        state: dict[str, Any] = {}

        if not getattr(self, "is_active", True):
            return

        def update_state(clss):
            for name, cls in inspect.getmembers(clss, predicate=inspect.isclass):
                o = getattr(self, name)
                if o is None or name.startswith("_") or name.startswith("__"):
                    continue

                # if issubclass(cls, PyReferenceObject):
                #     if o.LOCATION == "local":
                #         o = o.ref
                #     else:
                #         continue
                if issubclass(cls, PyLocalCommand):
                    args = {}
                    for arg in o._args:
                        args[arg] = getattr(o, arg)()
                    state[name] = args
                if issubclass(cls, PyLocalObject):
                    if getattr(o, "is_active", True):
                        state[name] = o(show_attributes)
                elif issubclass(cls, PyLocalNamedObject):
                    container = getattr(self, cls.PLURAL)
                    if getattr(container, "is_active", True):
                        state[cls.PLURAL] = {}
                        for child_name in container:
                            o = container[child_name]
                            if getattr(o, "is_active", True):
                                state[cls.PLURAL][child_name] = o()

                elif issubclass(cls, PyLocalProperty):
                    if getattr(o, "is_active", True):
                        state[name] = o()
                        attrs = show_attributes and getattr(o, "attributes", None)
                        if attrs:
                            for attr in attrs:
                                state[name + "." + attr] = getattr(o, attr)

            for base_class in clss.__bases__:
                update_state(base_class)

        update_state(self.__class__)
        return state

    __call__ = get_state

    def __setattr__(self, name: str, value: Any):
        attr = getattr(self, name, None)
        if attr and isinstance(attr, PyLocalProperty):
            attr.set_state(value)
        else:
            object.__setattr__(self, name, value)


CallKwargs = TypeVar("CallKwargs", bound=TypedDict)


class PyLocalCommand(PyLocalObject[ParentT], Generic[ParentT, CallKwargs], ABC):
    """Local object metaclass."""

    def __init__(self, parent: ParentT, api_helper: type[PostAPIHelper], name: str = ""):
        self._parent = parent
        self._name = name
        self._api_helper = api_helper(self)
        self.type = "object"
        self._args = []
        self._command_names = []

    @abstractmethod
    def _exe_cmd(self, **kwargs: Unpack[CallKwargs]) -> Any:
        """Execute command."""
        raise NotImplementedError("not implemented")

    def _update(self, api_helper: type[PostAPIHelper]) -> None:
        def update(clss) -> None:
            for name, cls in inspect.getmembers(clss, predicate=inspect.isclass):
                if issubclass(cls, PyLocalProperty):
                    self._args.append(name)
                    setattr(
                        self,
                        name,
                        cls(self, api_helper, name),
                    )
            for base_class in clss.__bases__:
                update(base_class)

    def __call__(self, **kwargs: Unpack[CallKwargs]):
        for arg_name, arg_value in kwargs.items():
            getattr(self, arg_name).set_state(arg_value)
        cmd_args = {}
        for arg_name in self._args:
            cmd_args[arg_name] = getattr(self, arg_name)()
        return self._exe_cmd(**cmd_args)


class PyLocalNamedObject(PyLocalObject[ParentT]):
    """Base class for local named object classes."""

    def __init__(self, name: str, parent: ParentT, api_helper: type[PostAPIHelper]):
        self._name = name
        self._api_helper = api_helper(self)
        self._parent = parent
        self._command_names = []
        self.type = "object"

        def update(clss):
            for name, cls in inspect.getmembers(clss, predicate=inspect.isclass):
                if issubclass(cls, PyLocalCommand):
                    self._command_names.append(name)

                if issubclass(cls, (PyLocalProperty, PyLocalObject, PyLocalCommand)):
                    # delete old property if overridden
                    if getattr(self, name).__name__ == name:
                        delattr(self, name)
                    setattr(
                        self,
                        name,
                        cls(self, api_helper, name),
                    )
                elif issubclass(cls, PyLocalNamedObject):
                    setattr(
                        self,
                        cls.PLURAL,
                        PyLocalContainer(self, cls, api_helper, cls.PLURAL),
                    )
                # elif issubclass(cls, PyReferenceObject):
                #     setattr(self, name, cls(self, cls.PATH, cls.LOCATION, cls.SESSION))
            for base_class in clss.__bases__:
                update(base_class)

        update(self.__class__)

    if TYPE_CHECKING:

        def create(self) -> Self: ...



DefnT = TypeVar("DefnT", bound=Defns, default=Defns)


def if_type_checking_instantiate(
    type: type[T],
) -> T:  # the current behaviour has all of the classes that use this initialised in the XXX class
    return cast(T, type)  # this is hopefully obviously unsafe


class _DeleteKwargs(TypedDict, total=False):
    names: list[str]


class _CreateKwargs(TypedDict, total=False):
    name: str | None


class PyLocalContainer(MutableMapping[str, DefnT]):
    """Local container for named objects."""

    def __init__(
        self,
        parent: "Container",
        object_class: type[PyLocalNamedObject[Any]],
        api_helper: type[PostAPIHelper],
        name: str = "",
    ):
        """Initialize the 'PyLocalContainer' object."""
        self._parent = parent
        self._name = name
        self.__object_class = object_class
        self._local_collection: dict[str, DefnT] = {}
        self.__api_helper = api_helper
        self.type = "named-object"
        self._command_names = []

        if hasattr(object_class, "SHOW_AS_SEPARATE_OBJECT"):
            PyLocalContainer.show_as_separate_object = property(
                lambda self: self.__object_class.SHOW_AS_SEPARATE_OBJECT(self)
            )
        if hasattr(object_class, "EXCLUDE"):
            PyLocalContainer.exclude = property(
                lambda self: self.__object_class.EXCLUDE(self)
            )
        if hasattr(object_class, "INCLUDE"):  # TODO sort_by?
            PyLocalContainer.include = property(
                lambda self: self.__object_class.INCLUDE(self)
            )
        if hasattr(object_class, "LAYOUT"):
            PyLocalContainer.layout = property(
                lambda self: self.__object_class.LAYOUT(self)
            )
        if hasattr(object_class, "STYLE"):
            PyLocalContainer.style = property(
                lambda self: self.__object_class.STYLE(self)
            )
        if hasattr(object_class, "ICON"):
            PyLocalContainer.icon = property(
                lambda self: self.__object_class.ICON(self)
            )
        if hasattr(object_class, "IS_ACTIVE"):
            PyLocalContainer.is_active = property(
                lambda self: self.__object_class.IS_ACTIVE(self)
            )

        for name, cls in inspect.getmembers(self.__class__, predicate=inspect.isclass):
            if issubclass(cls, PyLocalCommand):
                self._command_names.append(name)
                setattr(
                    self,
                    name,
                    cls(self, api_helper, name),
                )

    def get_root(self, obj=None):
        """Returns the top-most parent object."""
        obj = self if obj is None else obj
        parent = obj
        if getattr(obj, "_parent", None):
            parent = self.get_root(obj._parent)
        return parent

    def get_session(self, obj=None) -> "Solver":
        """Returns the session object."""
        root = self.get_root(obj)
        return root.session

    def get_path(self) -> str:
        """Path to the current object."""
        if getattr(self, "_parent", None):
            return self._parent.get_path() + "/" + self._name
        return self._name

    @property
    def path(self) -> str:
        """Path to the current object."""
        return self.get_path()

    @property
    def session(self) -> "Solver":
        """Returns the session object."""
        return self.get_session()

    @override
    def __iter__(self) -> Iterator[str]:
        return iter(self._local_collection)

    @override
    def __len__(self) -> int:
        return len(self._local_collection)

    @override
    def __getitem__(self, name: str) -> DefnT:
        o = self._local_collection.get(name, None)
        if not o:
            o = self._local_collection[name] = self.__object_class(
                name, self, self.__api_helper
            )
            on_create = getattr(self.__object_class, "on_create", None)
            if on_create:
                on_create(self, name)
        return o

    @override
    def __setitem__(self, name: str, value: DefnT) -> None:
        o = self[name]
        o.update(value)

    @override
    def __delitem__(self, name: str) -> None:
        del self._local_collection[name]
        on_delete = getattr(self.__object_class, "on_delete", None)
        if on_delete:
            on_delete(self, name)

    def _get_unique_child_name(self) -> str:
        children = list(self)
        index = 0
        while True:
            unique_name = f"{self.__object_class.__name__.lower()}-{index}"
            if unique_name not in children:
                break
            index += 1
        return unique_name

    class Delete(PyLocalCommand["PyLocalContainer", _DeleteKwargs]):
        """Local delete command."""

        @override
        def _exe_cmd(self, names: list[str]) -> None:
            for item in names:
                self._parent.__delitem__(item)

        @if_type_checking_instantiate
        class names(PyLocalProperty["Delete", list[str]]):
            """Local names property."""

            value = []

            @Attribute
            def allowed_values(self):
                """Get allowed values."""
                return list(self._parent._parent)

    class Create(PyLocalCommand["PyLocalContainer", _CreateKwargs]):
        """Local create command."""

        @override
        def _exe_cmd(self, name: str | None = None):
            if name is None:
                name = self._parent._get_unique_child_name()
            new_object = self._parent[name]
            return new_object._name

        @if_type_checking_instantiate
        class name(PyLocalProperty["Create", str | None]):
            """Local name property."""

            value = None

    # added by __init__
    delete: Delete
    create: Create
