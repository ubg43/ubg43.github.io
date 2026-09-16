from pathlib import Path
import re

FILES = [Path('index.html'), Path('legacy-index.html')]

CSS = r'''<style id="ubg43-final-layout-style">
/* Keep one homepage hero: the older legacy hero duplicates the V3 hero content. */
.hero { display: none !important; }

/* The stat pill is the compact home-page feature line. */
.hero-copy .hero-stat {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px !important;
  max-width: min(100%, 920px) !important;
  margin: 14px auto 0 !important;
  padding: 9px 15px !important;
  border-radius: 999px !important;
  background: linear-gradient(135deg, rgba(37,109,255,.26), rgba(139,92,246,.18)) !important;
  border: 1px solid rgba(255,255,255,.20) !important;
  color: #fff !important;
  box-shadow: 0 8px 22px rgba(0,27,90,.22), inset 0 1px 0 rgba(255,255,255,.10) !important;
  font-size: 12px !important;
  line-height: 1.35 !important;
  text-align: center !important;
}
</style>'''

JS = r'''<script id="ubg43-final-layout-runtime">
(()=>{
  'use strict';
  const desired = '1000+ games • fast search • automatic categories • new-game ribbons • trending picks • rotating homepage';
  function clean(){
    document.querySelectorAll('.hero-copy .hero-stat').forEach(p=>p.textContent = desired);
  }
  clean();
  setTimeout(clean, 100);
  setTimeout(clean, 500);
  setTimeout(clean, 1200);
})();
</script>'''

for p in FILES:
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    # Remove the legacy hero markup from the HTML itself, not just with CSS.
    text = re.sub(r'\s*<section\s+class=["\']hero["\'][^>]*>.*?</section>\s*', '\n', text, flags=re.I|re.S)
    text = re.sub(r'\s*<div\s+class=["\']hero["\'][^>]*>.*?</div>\s*', '\n', text, flags=re.I|re.S)
    # Keep this final patch idempotent.
    text = re.sub(r'\s*<style id="ubg43-final-layout-style">.*?</style>\s*', '\n', text, flags=re.S)
    text = re.sub(r'\s*<script id="ubg43-final-layout-runtime">.*?</script>\s*', '\n', text, flags=re.S)
    pos = text.lower().rfind('</head>')
    if pos != -1:
        text = text[:pos] + CSS + '\n' + text[pos:]
    pos = text.lower().rfind('</body>')
    if pos != -1:
        text = text[:pos] + JS + '\n' + text[pos:]
    p.write_text(text, encoding='utf-8')
    print('FINAL LAYOUT FIX:', p)
