from collections.abc import Sequence
from xml.etree.ElementTree import Element, SubElement, tostring
from app.models.pokemon import Pokemon


def _text(parent: Element, tag: str, value: object | None) -> None:
    SubElement(parent, tag).text = "" if value is None else str(value)


def _bool(parent: Element, tag: str, value: bool) -> None:
    SubElement(parent, tag).text = "true" if value else "false"


def _list(parent: Element, container_tag: str, item_tag: str, items: list[str] | None) -> None:
    container = SubElement(parent, container_tag)
    for it in (items or []):
        SubElement(container, item_tag).text = it


def _dict(parent: Element, container_tag: str, item_tag: str, items: dict[str, int] | None) -> None:
    container = SubElement(parent, container_tag)
    for k, v in (items or {}).items():
        SubElement(container, item_tag, attrib={"name": k}).text = str(v)


def _pokemon_node(root: Element, p: Pokemon) -> None:
    node = SubElement(root, "pokemon", attrib={"id": str(p.id), "name": p.name})

    _bool(node, "captured", p.captured)
    _text(node, "sprite", p.sprite)
    _text(node, "height", p.height)
    _text(node, "weight", p.weight)

    if p.description:
        _text(node, "description", p.description)
    if p.genus:
        _text(node, "genus", p.genus)

    _list(node, "types", "type", p.types)
    _list(node, "abilities", "ability", p.abilities)
    _dict(node, "stats", "stat", p.stats)
    _list(node, "weaknesses", "weakness", p.weaknesses)
    _list(node, "egg_groups", "egg_group", p.egg_groups)
    _list(node, "evolution_chain", "evolution", p.evolution_chain)


def pokemons_to_xml(pokemons: Sequence[Pokemon]) -> bytes:
    root = Element("pokedex")
    for p in pokemons:
        _pokemon_node(root, p)
    return tostring(root, encoding="utf-8", xml_declaration=True)