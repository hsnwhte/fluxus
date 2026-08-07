import json

from lxml import etree, html
from lxml.etree import ParserError, XMLSyntaxError

from pluggle.enums import ContentFormat
from pluggle.exceptions import errors
from pluggle.models.dto import TransformableData


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
