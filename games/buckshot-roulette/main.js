(() => {
  "use strict";

  const BASE = "https://raw.githubusercontent.com/fowntain/web-port-doge/main/buckshot-roulette/";
  const PCK_PARTS = 17;
  const WASM_PARTS = 3;
  const PCK_SIZE = 344705792;
  const WASM_SIZE = 43444261;

  function findGameFetch() {
    return typeof window.fetch === "function" ? window.fetch.bind(window) : fetch;
  }

  async function fetchPart(url, label) {
    const response = await findGameFetch()(url, { cache: "force-cache", mode: "cors" });
    if (!response.ok) throw new Error("Unable to load " + label + " (HTTP " + response.status + ")");
    return response;
  }

  function makeStream(prefix, count, padded, totalSize) {
    let part = 1;
    let remaining = 0;

    const stream = new ReadableStream({
      async pull(controller) {
        if (part > count) {
          controller.close();
          return;
        }
        try {
          const suffix = padded ? String(part).padStart(2, "0") : String(part);
          const response = await fetchPart(BASE + prefix + suffix, prefix + suffix);
          const buffer = await response.arrayBuffer();
          remaining += buffer.byteLength;
          controller.enqueue(new Uint8Array(buffer));
          part++;
        } catch (error) {
          controller.error(error);
        }
      }
    });

    return new Response(stream, {
      status: 200,
      headers: {
        "Content-Type": prefix.includes(".wasm") ? "application/wasm" : "application/octet-stream",
        "Content-Length": String(totalSize)
      }
    });
  }

  async function start() {
    const originalFetch = window.fetch.bind(window);

    window.fetch = async function(input, ...args) {
      const url = typeof input === "string" ? input : (input && input.url) || "";

      if (url.endsWith("buckshot-roulette.pck")) {
        return makeStream("buckshot-roulette.pck.part", PCK_PARTS, false, PCK_SIZE);
      }

      if (url.endsWith("buckshot-roulette.wasm")) {
        return makeStream("buckshot-roulette.wasm.part", WASM_PARTS, false, WASM_SIZE);
      }

      return originalFetch(input, ...args);
    };

    // main.js is loaded before the Godot bootstrap script in the source HTML.
    // Wait for the bootstrap function instead of racing it.
    const deadline = Date.now() + 30000;
    while (typeof window.godotRunStart !== "function") {
      if (Date.now() >= deadline) {
        throw new Error("Buckshot Roulette engine did not initialize.");
      }
      await new Promise(resolve => setTimeout(resolve, 25));
    }
    window.godotRunStart();
  }

  start().catch(error => {
    console.error("Buckshot Roulette loader error:", error);
    const status = document.getElementById("status-notice");
    const overlay = document.getElementById("status");
    if (status) {
      status.textContent = error && error.message ? error.message : "Unable to load Buckshot Roulette.";
      status.style.display = "block";
    }
    if (overlay) overlay.style.visibility = "visible";
  });
})();