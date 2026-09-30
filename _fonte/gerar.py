"""Gera as imagens SVG do README do perfil (banner, cards e tecnologias).

Uso: python gerar.py   (grava em ../assets)
Precisa de: pip install fonttools brotli, e a fonte em _fonte/SchibstedGrotesk.ttf
(https://github.com/google/fonts/tree/main/ofl/schibstedgrotesk).
A fonte Schibsted Grotesk vai embutida em cada SVG, só com os caracteres usados,
porque o GitHub não deixa uma imagem carregar fontes de fora.
"""
import base64
import io
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

AQUI = Path(__file__).parent
SAIDA = AQUI.parent / "assets"
FONTE = AQUI / "SchibstedGrotesk.ttf"

# Uma paleta só, escura: dentro de um link o GitHub não troca imagem por tema
# (ele tira o <picture> do link), então cada imagem precisa servir nos dois temas.
COR = {
    "fundo": "#0F2230", "borda": "#1F3B4F", "tinta": "#EDF4F2",
    "suave": "#A2B7BD", "fraco": "#4E6C7A", "acento": "#4CC9B5", "acento_leve": "#173E47",
}

PROJETOS = [
    {
        "arquivo": "projeto-ads-engine",
        "titulo": "AI Ad Engine",
        "texto": "Recebe os dados de um produto e escreve o anúncio para Mercado Livre, "
                 "Shopee ou Amazon: título, tópicos, descrição e palavras de busca.",
        "tecnologias": "TypeScript, Node.js, Express, SQLite, Llama 3.1",
        "acao": "Ler o estudo de caso",
        "desenho": "anuncio",
    },
    {
        "arquivo": "projeto-learn-english",
        "titulo": "Learn English",
        "texto": "App de vocabulário em inglês com 800 palavras em 16 temas e quatro jeitos "
                 "de praticar: forca, flashcards, quiz e pronúncia.",
        "tecnologias": "React, TypeScript, Vite, PWA",
        "acao": "Abrir o app",
        "desenho": "cartoes",
    },
    {
        "arquivo": "projeto-jornada-missionaria",
        "titulo": "Jornada Missionária",
        "texto": "Sistema de pontos de uma escola missionária, usado por 35 alunos: "
                 "ranking com pódio, lançamentos pela equipe e exportação para Excel.",
        "tecnologias": "Google Apps Script, Google Sheets, PWA",
        "acao": "Ver o repositório",
        "desenho": "podio",
    },
    {
        "arquivo": "projeto-rocketlog",
        "titulo": "Rocketlog",
        "texto": "API de entregas com cadastro, login por token, mudança de status "
                 "e histórico de cada pedido, com testes automatizados.",
        "tecnologias": "Node.js, Express, Prisma, PostgreSQL, Jest",
        "acao": "Ver o código",
        "desenho": "rota",
    },
]

CAMADAS = [
    ("Interface", ["HTML", "CSS", "React", "Tailwind CSS"]),
    ("Linguagens", ["JavaScript", "TypeScript"]),
    ("Servidor", ["Node.js", "Express", "Prisma", "Knex", "JWT", "Zod"]),
    ("Dados", ["PostgreSQL", "SQLite"]),
]
FERRAMENTAS = ("Ferramentas", ["Git", "Docker", "Vite", "Jest"])

BANNER = {
    "status": "Disponível para vagas",
    "nome": "Juan Pablo",
    "cargo": "Desenvolvedor fullstack júnior",
    "cidade": "Fortaleza, CE",
    "rotulo_a": "interface",
    "rotulo_b": "servidor",
}


class Fonte:
    """Um peso fixo da fonte variável: mede texto e gera o @font-face embutido."""

    def __init__(self, peso):
        self.peso = peso
        self.ttf = instantiateVariableFont(TTFont(FONTE), {"wght": peso})
        self.cmap = self.ttf.getBestCmap()
        self.hmtx = self.ttf["hmtx"]
        self.upm = self.ttf["head"].unitsPerEm

    def largura(self, texto, tamanho, espacamento=0):
        unidades = sum(self.hmtx[self.cmap[ord(c)]][0] for c in texto)
        return unidades * tamanho / self.upm + espacamento * len(texto)

    def font_face(self, caracteres):
        fonte = TTFont(io.BytesIO(self._bytes()))
        opcoes = Options()
        opcoes.flavor = "woff2"
        opcoes.layout_features = ["kern", "liga"]
        sub = Subsetter(opcoes)
        sub.populate(text="".join(sorted(set(caracteres))))
        sub.subset(fonte)
        buf = io.BytesIO()
        fonte.flavor = "woff2"
        fonte.save(buf)
        dados = base64.b64encode(buf.getvalue()).decode()
        return (f"@font-face{{font-family:SG;font-weight:{self.peso};"
                f"src:url(data:font/woff2;base64,{dados}) format('woff2')}}")

    def _bytes(self):
        buf = io.BytesIO()
        self.ttf.save(buf)
        return buf.getvalue()


PESOS = {p: Fonte(p) for p in (500, 700, 800)}


def esc(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def quebrar(texto, fonte, tamanho, largura_max):
    linhas, atual = [], ""
    for palavra in texto.split():
        tentativa = f"{atual} {palavra}".strip()
        if atual and fonte.largura(tentativa, tamanho) > largura_max:
            linhas.append(atual)
            atual = palavra
        else:
            atual = tentativa
    return linhas + [atual]


class Svg:
    """Junta os elementos e os textos de cada peso para embutir só o necessário."""

    def __init__(self, largura, altura, titulo):
        self.largura, self.altura, self.titulo = largura, altura, titulo
        self.partes, self.css = [], []
        self.usados = {p: set() for p in PESOS}

    def add(self, trecho):
        self.partes.append(trecho)

    def texto(self, x, y, conteudo, tamanho, peso, cor, espacamento=0, extra=""):
        self.usados[peso].update(conteudo)
        ls = f' letter-spacing="{espacamento}"' if espacamento else ""
        self.add(f'<text x="{x}" y="{y}" font-size="{tamanho}" font-weight="{peso}" '
                 f'fill="{cor}"{ls}{extra}>{esc(conteudo)}</text>')

    def salvar(self, nome):
        faces = [PESOS[p].font_face(c) for p, c in self.usados.items() if c]
        estilo = "".join(faces) + "text{font-family:SG,'Segoe UI',Helvetica,Arial,sans-serif}" + "".join(self.css)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.largura}" height="{self.altura}" '
               f'viewBox="0 0 {self.largura} {self.altura}" role="img" aria-label="{esc(self.titulo)}">'
               f"<title>{esc(self.titulo)}</title><style>{estilo}</style>"
               + "".join(self.partes) + "</svg>")
        (SAIDA / f"{nome}.svg").write_text(svg, encoding="utf-8")


def gerar_banner():
    """Banner com o nome e o desenho do navegador ligado ao servidor."""
    s = Svg(1280, 440, f"{BANNER['nome']}, {BANNER['cargo'].lower()} em {BANNER['cidade']}")
    fio = "M889 272 C889 392, 1139 392, 1139 272"
    s.css.append(
        "@keyframes pulso{0%{transform:scale(1);opacity:.55}100%{transform:scale(2.8);opacity:0}}"
        ".pulso{transform-origin:80px 118px;transform-box:view-box;animation:pulso 2.2s ease-out infinite}"
        "@media (prefers-reduced-motion:reduce){.pulso,.pacote{display:none}}"
    )
    s.add('<defs>'
          '<pattern id="pontos" width="26" height="26" patternUnits="userSpaceOnUse">'
          '<circle cx="2" cy="2" r="1.3" fill="#4CC9B5"/></pattern>'
          '<linearGradient id="some" x1="0" x2="1"><stop offset=".35" stop-color="#fff" stop-opacity="0"/>'
          '<stop offset="1" stop-color="#fff" stop-opacity=".22"/></linearGradient>'
          '<mask id="mascara"><rect width="1280" height="440" fill="url(#some)"/></mask>'
          '<clipPath id="canto"><rect width="1280" height="440" rx="24"/></clipPath>'
          '</defs>')
    s.add('<g clip-path="url(#canto)"><rect width="1280" height="440" fill="#0F2230"/>'
          '<rect width="1280" height="440" fill="url(#pontos)" mask="url(#mascara)"/></g>')

    # Texto
    s.add('<circle class="pulso" cx="80" cy="118" r="7" fill="#34D399"/>')
    s.add('<circle cx="80" cy="118" r="7" fill="#34D399"/>')
    s.texto(100, 126, BANNER["status"], 22, 500, "#A7E8DA")
    s.texto(68, 252, BANNER["nome"], 124, 800, "#F4F8F7", espacamento=-4)
    s.texto(74, 316, BANNER["cargo"], 32, 500, "#B3C7CC")
    s.texto(74, 358, BANNER["cidade"], 32, 500, "#6F8C96")

    # Desenho: navegador ligado ao servidor por um fio; um pacote vai e volta
    s.texto(794, 104, BANNER["rotulo_a"], 20, 500, "#6F8C96")
    s.texto(1064, 104, BANNER["rotulo_b"], 20, 500, "#6F8C96")
    traco = 'fill="none" stroke="#4CC9B5" stroke-width="2"'
    s.add(f'<rect x="794" y="124" width="190" height="148" rx="12" {traco} stroke-opacity=".7"/>'
          '<line x1="794" y1="150" x2="984" y2="150" stroke="#4CC9B5" stroke-opacity=".35" stroke-width="2"/>'
          + "".join(f'<circle cx="{810 + i * 13}" cy="137" r="3.5" fill="#4CC9B5" fill-opacity=".5"/>' for i in range(3))
          + '<rect x="812" y="170" width="112" height="12" rx="6" fill="#EDF4F2" fill-opacity=".85"/>'
          '<rect x="812" y="194" width="152" height="8" rx="4" fill="#A2B7BD" fill-opacity=".4"/>'
          '<rect x="812" y="210" width="128" height="8" rx="4" fill="#A2B7BD" fill-opacity=".4"/>')
    s.add('<rect x="812" y="234" width="72" height="22" rx="11" fill="#0B7F72">'
          '<animate attributeName="fill" values="#0B7F72;#0B7F72;#4CC9B5;#0B7F72" '
          'keyTimes="0;.82;.88;1" dur="4.8s" repeatCount="indefinite"/></rect>')
    for i in range(3):
        y = 124 + i * 52
        s.add(f'<rect x="1064" y="{y}" width="150" height="42" rx="9" {traco} stroke-opacity=".7"/>'
              f'<rect x="1080" y="{y + 17}" width="64" height="8" rx="4" fill="#A2B7BD" fill-opacity=".4"/>')
        acende = ('<animate attributeName="fill-opacity" values=".35;.35;1;1;.35;.35" '
                  f'keyTimes="0;{.36 + i * .02:.2f};{.40 + i * .02:.2f};{.50 + i * .02:.2f};{.56 + i * .02:.2f};1" '
                  'dur="4.8s" repeatCount="indefinite"/>')
        s.add(f'<circle cx="1196" cy="{y + 21}" r="5" fill="#34D399" fill-opacity=".35">{acende}</circle>')
    s.add(f'<path d="{fio}" fill="none" stroke="#2F5566" stroke-width="3" stroke-linecap="round" stroke-dasharray="1 11"/>')
    s.add('<circle class="pacote" r="7" fill="#7FE3D2">'
          f'<animateMotion path="{fio}" dur="4.8s" repeatCount="indefinite" calcMode="spline" '
          'keyPoints="0;1;1;0;0" keyTimes="0;.36;.5;.84;1" '
          'keySplines=".45 0 .25 1;0 0 1 1;.45 0 .25 1;0 0 1 1"/></circle>')
    s.salvar("banner")


def desenho(nome, t):
    """Ilustração pequena no canto de cada card (área de 440..566 x 34..116)."""
    a, leve, fraco, tinta = t["acento"], t["acento_leve"], t["fraco"], t["tinta"]
    if nome == "anuncio":
        return (f'<rect x="442" y="52" width="46" height="46" rx="8" fill="{leve}" stroke="{a}" stroke-width="2"/>'
                f'<path d="M452 66 L465 60 L478 66 L478 84 L465 90 L452 84 Z M452 66 L465 72 L478 66 M465 72 L465 90" '
                f'fill="none" stroke="{a}" stroke-width="2" stroke-linejoin="round"/>'
                + "".join(f'<circle cx="{498 + i * 8}" cy="75" r="2" fill="{fraco}"/>' for i in range(3))
                + f'<rect x="520" y="36" width="46" height="78" rx="7" fill="none" stroke="{tinta}" stroke-opacity=".5" stroke-width="2"/>'
                f'<rect x="528" y="46" width="30" height="7" rx="3.5" fill="{a}"/>'
                + "".join(f'<rect x="528" y="{62 + i * 10}" width="{30 - (i % 2) * 8}" height="5" rx="2.5" fill="{fraco}"/>' for i in range(4)))
    if nome == "cartoes":
        return (f'<g transform="rotate(9 520 78)"><rect x="470" y="40" width="96" height="66" rx="9" fill="{leve}" stroke="{a}" stroke-opacity=".6" stroke-width="2"/></g>'
                f'<g transform="rotate(-6 500 78)"><rect x="446" y="44" width="100" height="68" rx="9" fill="{t["fundo"]}" stroke="{a}" stroke-width="2"/></g>')
    if nome == "podio":
        blocos = [(452, 64, 2), (492, 46, 1), (532, 78, 3)]
        partes = []
        for x, y, pos in blocos:
            cor = a if pos == 1 else leve
            partes.append(f'<rect x="{x}" y="{y}" width="36" height="{114 - y}" rx="5" fill="{cor}"/>')
        partes.append(f'<path d="M497 38 L500 28 L510 34 L520 28 L523 38 Z" fill="{a}"/>')
        return "".join(partes)
    if nome == "rota":
        caminho = "M446 104 C476 104, 470 56, 506 60 S536 104, 562 44"
        return (f'<path d="{caminho}" fill="none" stroke="{fraco}" stroke-width="2.5" stroke-dasharray="1 7" stroke-linecap="round"/>'
                f'<circle cx="446" cy="104" r="6" fill="{a}"/>'
                f'<circle cx="506" cy="60" r="6" fill="{a}"/>'
                f'<circle cx="562" cy="44" r="8" fill="{t["fundo"]}" stroke="{a}" stroke-width="2.5"/>'
                f'<circle cx="562" cy="44" r="2.5" fill="{a}"/>')
    raise ValueError(nome)


def gerar_card(projeto):
    t = COR
    s = Svg(600, 340, f"{projeto['titulo']}: {projeto['texto']}")
    s.add(f'<rect x="1" y="1" width="598" height="338" rx="18" fill="{t["fundo"]}" stroke="{t["borda"]}" stroke-width="2"/>')
    s.add(desenho(projeto["desenho"], t))
    if projeto["desenho"] == "cartoes":  # palavras dos flashcards
        s.add('<g transform="rotate(-6 500 78)">')
        s.texto(462, 80, "apple", 24, 800, t["tinta"])
        s.texto(462, 101, "maçã", 16, 500, t["suave"])
        s.add("</g>")

    tamanho_titulo = 34
    while PESOS[800].largura(projeto["titulo"], tamanho_titulo, -0.5) > 380:
        tamanho_titulo -= 1
    s.texto(36, 92, projeto["titulo"], tamanho_titulo, 800, t["tinta"], espacamento=-0.5)

    for i, linha in enumerate(quebrar(projeto["texto"], PESOS[500], 20, 528)):
        s.texto(36, 146 + i * 30, linha, 20, 500, t["suave"])
    s.texto(36, 268, projeto["tecnologias"], 18, 700, t["suave"], extra=' fill-opacity=".8"')
    s.texto(36, 306, projeto["acao"], 20, 700, t["acento"])
    s.salvar(projeto["arquivo"])


def gerar_tecnologias():
    """As camadas de cima para baixo, da interface aos dados, ligadas por uma linha."""
    t = COR
    altura_linha, topo = 64, 56
    s = Svg(1200, 400, "Tecnologias: " + "; ".join(f"{n}: {', '.join(i)}" for n, i in CAMADAS + [FERRAMENTAS]))
    s.add(f'<rect x="1" y="1" width="1198" height="398" rx="18" fill="{t["fundo"]}" stroke="{t["borda"]}" stroke-width="2"/>')
    ultimo = topo + (len(CAMADAS) - 1) * altura_linha
    s.add(f'<line x1="56" y1="{topo}" x2="56" y2="{ultimo}" stroke="{t["acento"]}" stroke-width="3"/>')

    def linha(y, nome, itens, cheio):
        if cheio:
            s.add(f'<circle cx="56" cy="{y}" r="9" fill="{t["acento"]}"/>')
        else:
            s.add(f'<circle cx="56" cy="{y}" r="8" fill="{t["fundo"]}" stroke="{t["fraco"]}" stroke-width="3"/>')
        s.texto(88, y + 8, nome, 23, 700, t["tinta"])
        x = 300
        for item in itens:
            s.texto(x, y + 8, item, 23, 500, t["suave"])
            x += PESOS[500].largura(item, 23) + 40

    for i, (nome, itens) in enumerate(CAMADAS):
        linha(topo + i * altura_linha, nome, itens, True)
    s.add(f'<line x1="36" y1="{ultimo + 46}" x2="1164" y2="{ultimo + 46}" stroke="{t["borda"]}" stroke-width="2"/>')
    linha(ultimo + 94, *FERRAMENTAS, False)
    s.salvar("tecnologias")


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    gerar_banner()
    for projeto in PROJETOS:
        gerar_card(projeto)
    gerar_tecnologias()
    for arquivo in sorted(SAIDA.glob("*.svg")):
        print(f"{arquivo.name:40} {arquivo.stat().st_size // 1024} KB")
