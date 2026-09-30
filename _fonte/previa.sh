#!/usr/bin/env bash
# Renderiza o README pela API do GitHub e monta previa.html com o visual do GitHub.
set -euo pipefail
cd "$(dirname "$0")/.."
corpo=$(gh api markdown -f mode=markdown -f context=juanpablolpf/juanpablolpf -f text="$(cat README.md)")
cat > previa.html <<HTML
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prévia do perfil</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.8.1/github-markdown.min.css">
<style>
body{margin:0;background:#fff}
@media (prefers-color-scheme:dark){body{background:#0d1117}}
.markdown-body{box-sizing:border-box;max-width:880px;margin:24px auto;padding:24px;border:1px solid #d0d7de;border-radius:6px}
@media (prefers-color-scheme:dark){.markdown-body{border-color:#30363d}}
</style></head><body><article class="markdown-body">
$corpo
</article>
<script>
// Imita o <themed-picture> do GitHub: no tema escuro, usa a imagem do <source>.
if (matchMedia("(prefers-color-scheme: dark)").matches) {
  document.querySelectorAll("themed-picture").forEach((tp) => {
    const fonte = tp.querySelector("source"), img = tp.querySelector("img");
    if (fonte && img) img.src = fonte.getAttribute("srcset");
  });
}
</script></body></html>
HTML
echo "ok: previa.html"
