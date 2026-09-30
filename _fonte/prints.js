// Tira prints da prévia nos temas claro/escuro e na largura de celular.
const path = require("path");
const { chromium } = require(path.join(process.env.USERPROFILE, "Desktop/Arroba/gerador/node_modules/playwright-core"));

(async () => {
  const browser = await chromium.launch({ channel: "chrome" });
  const url = require("url").pathToFileURL(path.resolve(__dirname, "../previa.html")).href;
  const saida = process.argv[2];
  for (const [nome, tema, largura] of [["claro", "light", 1280], ["escuro", "dark", 1280], ["celular", "dark", 390]]) {
    const page = await browser.newPage({ colorScheme: tema, viewport: { width: largura, height: 900 } });
    await page.goto(url);
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(saida, `previa-${nome}.png`), fullPage: true });
    await page.close();
  }
  await browser.close();
})();
