from pathlib import Path

INDEX = Path('index.html')

CSS = '''<style id="loading-polish-style">
  .loading-card.loading-state{
    min-height:150px;
    margin:22px;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-direction:column;
    gap:12px;
    background:rgba(255,255,255,.96);
    color:#5e6b82;
  }
  .loading-spinner{
    width:36px;
    height:36px;
    border:4px solid #dbe5f5;
    border-top-color:#0047bd;
    border-radius:50%;
    animation:ubgSpin .8s linear infinite;
    box-shadow:0 3px 10px rgba(0,34,102,.10);
  }
  .loading-label{font-size:14px;font-weight:750;letter-spacing:.01em}
  @keyframes ubgSpin{to{transform:rotate(360deg)}}
</style>\n'''

index = INDEX.read_text(encoding='utf-8')

if 'id="loading-polish-style"' not in index:
    index = index.replace('</head>', CSS + '</head>', 1)

old = '<div id="loadingCard" class="loading-card">Loading games...</div>'
new = '<div id="loadingCard" class="loading-card loading-state" role="status" aria-live="polite"><span class="loading-spinner" aria-hidden="true"></span><span class="loading-label">Loading games...</span></div>'
if old in index:
    index = index.replace(old, new, 1)
else:
    # Keep the loader visible even if an earlier version already has a custom loading wrapper.
    index = index.replace('id="loadingCard" class="loading-card"', 'id="loadingCard" class="loading-card loading-state"', 1)

INDEX.write_text(index, encoding='utf-8')
print('LOADING POLISH: added centered animated loader for initial game-library fetch.')
