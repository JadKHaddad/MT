for f in mermaid/*.mmd; do
   mmdc -i "$f" -o "mermaid/svg/$(basename "${f%.mmd}.svg")" -c mermaid/mermaid-config.json
done

for f in mermaid/svg/*.svg; do
   rsvg-convert -f pdf -o "img/mermaid/$(basename "${f%.svg}.pdf")" "$f"
done