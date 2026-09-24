import { chromium } from "playwright";

const targets = [
  ["steal", "https://app-580426.cdn.games.yandex.net/580426/pr8news651eea9ccyvedugx9c5ce1st4_brotli/index.html"],
  ["meccha", "https://app-593207.cdn.games.yandex.net/593207/7mufd9blfjva1kvmagdoyg7krmngdw6k_brotli/index.html"],
  ["rivals", "https://veck.io/"]
];

const browser = await chromium.launch({headless:true,args:["--no-sandbox","--disable-dev-shm-usage"]});
for (const [name,url] of targets) {
  const page = await browser.newPage({viewport:{width:1440,height:900}});
  const errors = [];
  page.on("pageerror", e => errors.push(String(e)));
  page.on("console", m => { if (m.type()==="error") errors.push(m.text()); });
  await page.setContent('<!doctype html><html><body style="margin:0"><iframe id="game" src="'+url+'" style="position:fixed;inset:0;width:100%;height:100%;border:0"></iframe></body></html>');
  await page.waitForTimeout(10000);
  const frames = page.frames().map(f => ({url:f.url(), name:f.name()}));
  const frameInfo = [];
  for (const f of page.frames().slice(1)) {
    try {
      frameInfo.push({
        url:f.url(),
        title:await f.title().catch(()=> ""),
        body:(await f.locator("body").innerText().catch(()=> "")).slice(0,1200)
      });
    } catch {}
  }
  for (const f of page.frames().slice(1)) { try { console.log("HTML "+name+" "+JSON.stringify((await f.content()).slice(0,14000))); } catch {} }
  console.log(JSON.stringify({name,url,finalPageUrl:page.url(),frameCount:page.frames().length,frames,frameInfo,errors:errors.slice(0,20)}));
  await page.close();
}
await browser.close();
