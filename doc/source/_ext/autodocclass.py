from enum import IntEnum
from typing import Any, Optional

from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.ext.autodoc import ClassDocumenter, bool_option


class PostDocumenter(ClassDocumenter):
    objtype = "postdoc"
    directivetype = ClassDocumenter.objtype
    priority = 10 + ClassDocumenter.priority
    option_spec = dict(ClassDocumenter.option_spec)
    option_spec["hex"] = bool_option

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        try:
            return issubclass(member, IntEnum)
        except TypeError:
            return False

    def add_directive_header(self, sig: str) -> None:
        self.add_line(f".. _post_{self.object.__name__}:", self.get_sourcename())
        self.add_line("   ", self.get_sourcename())
        super().add_directive_header(sig)
        self.add_line("   ", self.get_sourcename())

    def add_content(self, more_content: Optional[StringList]) -> None:

        super().add_content(more_content)

        source_name = self.get_sourcename()
        object = self.object
        self.add_line("", source_name)

        data_dicts = {}

        def _update(clss, obj_name, parent_name=None, parent_path=None):
            if not data_dicts.get(obj_name):
                data_dicts[obj_name] = {}
                data_dicts[obj_name]["parent"] = parent_name
                data_dicts[obj_name]["path"] = (
                    parent_path + "_" + obj_name if parent_path else obj_name
                )
                data_dicts[obj_name]["obj"] = clss
                data_dicts[obj_name]["attr"] = {"Member": "Summary"}
                data_dicts[obj_name]["cmd"] = {"Command": "Summary"}
                data_dicts[obj_name]["include"] = {"Parent": "Summary"}
            dic = data_dicts[obj_name]
            if parent_path:
                dic["include"][
                    f":ref:`{parent_name} <post_{parent_path}>`"
                ] = f"{parent_name}'s child"

            for the_member_name in dir(clss):
                if the_member_name.startswith("_"):
                    continue
                cls = getattr(clss, the_member_name)
                the_member_value = cls.__doc__.split("\n")[0]
                if cls.__class__.__name__ in (
                    "PyLocalPropertyMeta",
                    "PyLocalObjectMeta",
                ):
                    if cls.__class__.__name__ == "PyLocalObjectMeta":
                        dic["attr"][
                            f":ref:`{the_member_name} <post_{dic['path']}_{the_member_name}>`"  # noqa: E501
                        ] = the_member_value
                    else:
                        dic["attr"][the_member_name] = the_member_value
                        attrs = getattr(cls, "attributes", None)
                        if attrs:
                            for attr in attrs:
                                dic["attr"][
                                    f"{the_member_name}.{attr}"
                                ] = f"``{the_member_name}`` {' '.join(attr.split('_'))}."  # noqa: E501

                elif callable(cls):
                    dic["cmd"][the_member_name] = the_member_value

            for name in dir(clss):
                cls = getattr(clss, name)
                if cls.__class__.__name__ in ("PyLocalObjectMeta",):
                    _update(cls, name, obj_name, data_dicts[obj_name]["path"])
            for base_class in clss.__bases__:
                _update(base_class, obj_name, parent_name)

        _update(object, object.__name__)
        key_max = 0
        val_max = 0
        for obj_name, obj_dic in data_dicts.items():
            o = obj_dic["obj"]
            parent = obj_dic["parent"]
            for item in ["attr", "cmd", "include"]:
                dic = obj_dic[item]
                if len(dic) > 1:
                    key_max = max(key_max, len(max(dic.keys(), key=len)))
                    val_max = max(val_max, len(max(dic.values(), key=len)))

        for obj_name, obj_dic in data_dicts.items():
            o = obj_dic["obj"]
            parent = obj_dic["parent"]
            dic = obj_dic["attr"]
            if len(dic) > 1:
                col_gap = 3
                total = key_max + val_max + col_gap
                # Top border
                if o != object:
                    self.add_line(f".. _post_{obj_dic['path']}:", source_name)
                    self.add_line("", source_name)
                    self.add_line(
                        f".. rubric:: {o.__module__}.{o.__qualname__}", source_name
                    )
                    self.add_line("", source_name)
                    # self.add_line(
                    #    f".. autoclass:: {o.__module__}.{o.__qualname__}", source_name
                    # )
                self.add_line(f".. rubric:: Attributes", source_name)
                self.add_line("", source_name)
                self.add_line(f'{"="*key_max}{" "*col_gap}{"="*val_max}', source_name)
                header = True
                for key, value in dic.items():
                    if header:
                        # Write header and border
                        self.add_line(
                            f'{key}{" "*(total-len(key)-len(value))}{value}',
                            source_name,
                        )
                        self.add_line(
                            f'{"="*key_max}{" "*col_gap}{"="*val_max}', source_name
                        )
                        header = False
                    else:
                        # actual data
                        self.add_line(
                            f'{key}{" "*(total-len(key)-len(value))}{value}',
                            source_name,
                        )
                # Bottom border
                self.add_line(f'{"="*key_max}{" "*col_gap}{"="*val_max}', source_name)
                self.add_line("", source_name)

            dic = obj_dic["cmd"]
            if "update" in dic:
                del dic["update"]
            if len(dic) > 1:
                col_gap = 3
                total = key_max + val_max + col_gap

                self.add_line(f".. rubric:: Commands", source_name)
                self.add_line("", source_name)
                self.add_line(f'{"="*key_max}{" "*col_gap}{"="*val_max}', source_name)
                header = True
                for key, value in dic.items():
                    if header:
                        # Write header and border
                        self.add_line(
                            f'{key}{" "*(total-len(key)-len(value))}{value}',
                            source_name,
                        )
                        self.add_line(
                            f'{"="*key_max}{" "*col_gap}{"="*val_max}', source_name
                        )
                        header = False
                    else:
                        # actual data
                        self.add_line(
                            f'{key}{" "*(total-len(key)-len(value))}{value}',
                            source_name,
                        )
                # Bottom border
                self.add_line("", source_name)
                self.add_line(f'{"="*key_max}{" "*col_gap}{"="*val_max}', source_name)
                self.add_line("", source_name)
                self.add_line("", source_name)

            if parent:
                dic = obj_dic["include"]
                col_gap = 3
                total = key_max + val_max + col_gap

                self.add_line(f".. rubric:: Included in", source_name)
                self.add_line("   ", source_name)
                self.add_line(f'{"="*key_max}{" "*col_gap}{"="*val_max}', source_name)
                self.add_line("   ", source_name)
                header = True
                for key, value in dic.items():
                    if header:
                        # Write header and border
                        self.add_line(
                            f'{key}{" "*(total-len(key)-len(value))}{value}',
                            source_name,
                        )
                        self.add_line(
                            f'{"="*key_max}{" "*col_gap}{"="*val_max}', source_name
                        )
                        header = False
                    else:
                        # actual data
                        self.add_line(
                            f'{key}{" "*(total-len(key)-len(value))}{value}',
                            source_name,
                        )
                # Bottom border
                self.add_line("", source_name)
                self.add_line(f'{"="*key_max}{" "*col_gap}{"="*val_max}', source_name)
                self.add_line("", source_name)
            self.add_line("", source_name)


def setup(app: Sphinx) -> None:
    app.setup_extension("sphinx.ext.autodoc")  # Require autodoc extension
    app.add_autodocumenter(PostDocumenter)
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
