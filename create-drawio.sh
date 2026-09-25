python3 drawio/set_drawio_font.py drawio/*.drawio

for f in drawio/*.drawio; do
   drawio -x -f pdf --crop -o "img/drawio/$(basename "${f%.drawio}.pdf")" "$f" --disable-gpu
done