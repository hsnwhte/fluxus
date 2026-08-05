import json
from lxml import html, etree
from lxml.etree import XMLSyntaxError, ParserError

from fluxus.enums import ContentFormat
from fluxus.models.dto import TransformableData
from fluxus.exceptions import errors


def _element_to_dict(element: etree._Element):
    node = {"tag": element.tag}
    if element.attrib:
        node["attributes"] = dict(element.attrib)
    if element.text and element.text.strip():
        node["text"] = element.text.strip()
    children = [_element_to_dict(child) for child in element]
    if children:
        node["children"] = children
    return node


class HtmlExtractStrategy:
    @staticmethod
    def extract(*, content: bytes) -> TransformableData:
        try:
            tree = html.fromstring(content)
        except (XMLSyntaxError, ParserError) as e:
            raise errors.ExtractSyntaxError(f"Malformed HTML content: {e}") from e
        parsed = _element_to_dict(tree)
        content_bytes = json.dumps(parsed, ensure_ascii=False).encode()
        return TransformableData(
            content=content_bytes, origin_format=ContentFormat.HTML
        )
