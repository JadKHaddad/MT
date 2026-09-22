"""Set the font of every text element in .drawio files (edited in place).

Usage: python3 set_drawio_font.py drawio/*.drawio
"""

import base64
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib

FONT = "Times New Roman"


def decompress(text):
    data = base64.b64decode(text)
    xml = zlib.decompress(data, -15).decode("utf-8")
    return ET.fromstring(urllib.parse.unquote(xml))


def fix_style(style):
    if re.search(r"(^|;)fontFamily=", style):
        return re.sub(r"(^|;)fontFamily=[^;]*", rf"\1fontFamily={FONT}", style)
    if style and not style.endswith(";"):
        style += ";"
    return style + f"fontFamily={FONT};"


def fix_html(value):
    # Inline fonts inside HTML labels: <font face="..."> and style="font-family: ..."
    value = re.sub(r'face="[^"]*"', f'face="{FONT}"', value)
    value = re.sub(r'font-family:(?:&quot;|[^;"])*', f"font-family: {FONT}", value)
    return value


def process_model(model):
    for cell in model.iter("mxCell"):
        # Labels may live on the cell or on a wrapping <UserObject>/<object>
        if cell.get("value") or cell.get("style") is not None:
            cell.set("style", fix_style(cell.get("style", "")))
        if cell.get("value"):
            cell.set("value", fix_html(cell.get("value")))
    for obj in list(model.iter("UserObject")) + list(model.iter("object")):
        if obj.get("label"):
            obj.set("label", fix_html(obj.get("label")))


def process_file(path):
    tree = ET.parse(path)
    root = tree.getroot()
    for diagram in root.iter("diagram"):
        model = diagram.find("mxGraphModel")
        if model is None and diagram.text and diagram.text.strip():
            # Compressed diagram: unpack it and store it uncompressed
            model = decompress(diagram.text.strip())
            diagram.text = None
            diagram.append(model)
        if model is not None:
            process_model(model)
    if root.get("compressed"):
        root.set("compressed", "false")
    tree.write(path, encoding="utf-8", xml_declaration=False)
    print(f"{path}: font set to {FONT}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        process_file(p)
