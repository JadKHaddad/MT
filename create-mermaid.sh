for f in mermaid/*.mmd; do
   mmdc -i "$f" -o "img/mermaid/$(basename "${f%.mmd}.pdf")" -c mermaid/mermaid-config.json -b white
done