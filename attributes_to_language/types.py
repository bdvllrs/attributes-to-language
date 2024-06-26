from collections.abc import Callable, Mapping, MutableMapping, Sequence
from typing import Any, TypeAlias, TypedDict

ComputedAttributeT: TypeAlias = MutableMapping[str, str]
AttributeT: TypeAlias = Mapping[str, Any]
CallbackVariantT: TypeAlias = Callable[[ComputedAttributeT | None], str]
VariantT: TypeAlias = str | CallbackVariantT
VariantsT: TypeAlias = Mapping[str, Sequence[VariantT]]
ChoicesT: TypeAlias = MutableMapping[str, int]


class Choices(TypedDict, total=False):
    structure: int
    groups: list[int]
    writers: dict[str, dict[str, int]]
    variants: dict[str, int]
