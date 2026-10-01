# leap-website

Project page for **LEAP: Learned Block-wise Evidence Retrieval for Long Audio-Video Perception**.

Static site, served by GitHub Pages at <https://lukelin-web.github.io/leap-website/>.

```
index.html              the whole page
static/css/             bulma.min.css + index.css + leap.css (template from phyground.github.io / OpenVLA / Nerfies)
static/js/              fontawesome.all.min.js (button icons)
static/images/*.png        figures rendered from the paper's PDFs (pdftoppm -r 300)
static/leap.pdf         the paper
static/videos/          demo clips cut from the retained windows only (~4 MB total), with poster frames
tools/demos.json        the four demo questions: windows, evidence span, both systems' answers
tools/build_demos.py    renders the demo cards into index.html between the demos:start/end markers
.github/workflows/      deploys the repo root on every push to main
.nojekyll               serve the HTML verbatim
```

To update: edit `index.html`, replace a figure or the PDF under `static/`, then commit and push to `main`.
To change the demos: edit `tools/demos.json`, drop the clips under `static/videos/`, run `python3 tools/build_demos.py`.
