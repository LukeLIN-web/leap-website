# leap-website

Project page for **LEAP: Learned Block-wise Evidence Retrieval for Long Audio-Video Perception**.

Static site, served by GitHub Pages at <https://lukelin-web.github.io/leap-website/>.

```
index.html              the whole page
static/css/base.css     layout, derived from phyground.github.io (MIT)
static/img/*.png        figures rendered from the paper's PDFs (pdftoppm -r 300)
static/leap.pdf         the paper
.github/workflows/      deploys the repo root on every push to main
.nojekyll               serve the HTML verbatim
```

To update: edit `index.html`, replace a figure or the PDF under `static/`, then commit and push to `main`.
