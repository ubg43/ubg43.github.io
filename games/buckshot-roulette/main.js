(() => {
  "use strict";

  const base = "https://raw.githubusercontent.com/giorgirick2-gif/game-webports-onawebsite/main/buckshot-roulette/";
  const PARTS = Object.freeze({
    pck: 17,
    wasm: 3
  });

  const loadingText = () => document.getElementById("loading-text");
  const notice = () => document.getElementById("status-notice");
  const progress = () => document.getElementById("status-progress");
  const status = () => document.getElementById("status");

  function showError(error) {
    console.error("Buckshot Roulette load error:", error);
    const message = error instanceof Error ? error.message : String(error || "Unknown error");
    const el = notice();
    const overlay = status();
    const text = loadingText();
    if (text) text.textContent = "BUCKSHOT ROULETTE COULD NOT LOAD";
    if (overlay) overlay.style.visibility = "visible";
    if (progress()) progress().style.display = "none";
    if (el) {
      el.style.display = "block";
      el.textContent = "Load error: " + message;
    }
  }

  async function fetchPart(url, index, total) {
    const response = await fetch(url, { cache: "force-cache", mode: "cors" });
    if (!response.ok) {
      throw new Error("Missing game data part " + index + "/" + total + " (HTTP " + response.status + ")");
    }
    return new Uint8Array(await response.arrayBuffer());
  }

  async function mergeFile(name, count) {
    const urls = Array.from({ length: count }, (_, i) => base + name + ".part" + (i + 1));
    const parts = await Promise.all(urls.map((url, i) => fetchPart(url, i + 1, count)));
    const size = parts.reduce((total, part) => total + part.byteLength, 0);
    const merged = new Uint8Array(size);
    let offset = 0;
    for (const part of parts) {
      merged.set(part, offset);
      offset += part.byteLength;
    }
    return URL.createObjectURL(new Blob([merged], { type: "application/octet-stream" }));
  }

  async function waitForGodotRunner(timeoutMs = 15000) {
    const start = Date.now();
    while (typeof window.godotRunStart !== "function") {
      if (Date.now() - start > timeoutMs) {
        throw new Error("Godot game engine did not finish initializing.");
      }
      await new Promise(resolve => setTimeout(resolve, 25));
    }
  }

  async function start() {
    try {
      await waitForGodotRunner();

      const text = loadingText();
      const p = progress();
      if (text) text.textContent = "LOADING BUCKSHOT ROULETTE...";
      if (p) {
        p.style.display = "block";
        p.removeAttribute("value");
        p.removeAttribute("max");
      }

      const [pckUrl, wasmUrl] = await Promise.all([
        mergeFile("buckshot-roulette.pck", PARTS.pck),
        mergeFile("buckshot-roulette.wasm", PARTS.wasm)
      ]);

      const originalFetch = window.fetch;
      window.fetch = async (input, ...args) => {
        const url = typeof input === "string" ? input : input?.url || "";
        let pathname = url;
        try { pathname = new URL(url, location.href).pathname; } catch (_) {}
        if (pathname.endsWith("/buckshot-roulette.pck")) return originalFetch(pckUrl, ...args);
        if (pathname.endsWith("/buckshot-roulette.wasm")) return originalFetch(wasmUrl, ...args);
        return originalFetch(input, ...args);
      };

      window.addEventListener("pagehide", () => {
        try { URL.revokeObjectURL(pckUrl); } catch (_) {}
        try { URL.revokeObjectURL(wasmUrl); } catch (_) {}
      }, { once: true });

      window.godotRunStart();
    } catch (error) {
      showError(error);
    }
  }

  start();
})();
