# MT

## Install latex packages

```bash
sudo apt install texlive-science texlive-latex-extra texlive-extra-utils texlive-lang-german latexmk texlive-publishers texlive-science
```

## Install mermaid-cli

```bash
sudo npm install -g @mermaid-js/mermaid-cli
```

## Install librsvg2-bin (Convert svg to pdf)

```bash
sudo apt install librsvg2-bin
```

## Create mermaid diagrams

```bash
./create-mermaid.sh
```

## Note on build

We set `"latex-workshop.latex.outDir": "%DIR%/.build"` in `.vscode/settings.json` but latex does not create the `.build/tex/chapters` folder. So we have to create it manually.
