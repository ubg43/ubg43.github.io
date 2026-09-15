from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Refine game-card interaction and general button polish.
s = s.replace(
'''    .game-card{position:relative;background:rgba(255,255,255,.98);border-radius:14px;overflow:hidden;box-shadow:0 5px 16px rgba(0,0,0,.12);cursor:pointer;transition:transform .20s cubic-bezier(.2,.8,.2,1),box-shadow .20s ease}\n    .game-card:hover{transform:translateY(-6px) scale(1.025);box-shadow:0 15px 30px rgba(3,20,55,.24)}\n    .game-card img{display:block;width:100%;height:140px;object-fit:cover;transition:transform .22s ease,filter .22s ease}\n    .game-card:hover img{transform:scale(1.04);filter:saturate(1.05)}\n    .game-card h3{margin:10px 10px 12px;color:#172039;font-size:15px;line-height:1.3;text-align:center}''',
'''    .game-card{position:relative;background:rgba(255,255,255,.98);border-radius:15px;overflow:hidden;box-shadow:0 5px 16px rgba(0,0,0,.12);cursor:pointer;transition:transform .20s cubic-bezier(.2,.8,.2,1),box-shadow .20s ease,filter .20s ease}\n    .game-card::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:15px;border:1px solid rgba(255,255,255,.55);opacity:0;transition:opacity .18s ease}\n    .game-card:hover{transform:translateY(-6px) scale(1.025);box-shadow:0 17px 34px rgba(3,20,55,.27);filter:saturate(1.02)}\n    .game-card:hover::after{opacity:1}\n    .game-card:active{transform:translateY(-2px) scale(.995);box-shadow:0 9px 20px rgba(3,20,55,.22)}\n    .game-card img{display:block;width:100%;height:140px;object-fit:cover;transition:transform .24s cubic-bezier(.2,.8,.2,1),filter .24s ease}\n    .game-card:hover img{transform:scale(1.045);filter:saturate(1.08) contrast(1.015)}\n    .game-card h3{margin:10px 10px 12px;color:#172039;font-size:15px;line-height:1.3;text-align:center}'''
)

# Make the category toggle match the darker button treatment.
s = s.replace('background:#0849b6;color:#fff;font-size:13px;font-weight:800;cursor:pointer;', 'background:#0744ab;color:#fff;font-size:13px;font-weight:800;cursor:pointer;', 1)
s = s.replace('background:#063f9f;box-shadow:0 9px 21px', 'background:#063a92;box-shadow:0 9px 21px', 1)

# Add a restrained "glass" treatment and focus feedback to interactive controls.
anchor = '    .category-item.is-trending.is-active{background:rgba(28,94,205,.29);border-color:rgba(83,148,255,.42)}\n'
extra = '''    .category-item.is-trending.is-active{background:rgba(28,94,205,.29);border-color:rgba(83,148,255,.42)}\n    .header-action:focus-visible,.category-toggle:focus-visible,.category-close:focus-visible,.category-item:focus-visible,.recommendation-arrow:focus-visible,.search-clear:focus-visible,.search-result:focus-visible,.search-recommendation:focus-visible{outline:2px solid rgba(255,255,255,.92);outline-offset:2px}\n    .search-recommendation{transition:transform .18s cubic-bezier(.2,.8,.2,1),box-shadow .18s ease,filter .18s ease}\n    .search-recommendation:hover{filter:saturate(1.03);}\n    .search-recommendation:active{transform:translateY(-1px) scale(.995);}\n    .recommendation-arrow{backdrop-filter:blur(6px);}\n'''
if anchor not in s:
    raise SystemExit('category anchor not found')
s = s.replace(anchor, extra, 1)

# Upgrade the click sound from a single tiny tick into a soft two-note UI chime.
old = '''  function clickSound(){\n    try{\n      audioContext=audioContext||new(window.AudioContext||window.webkitAudioContext)();\n      if(audioContext.state==='suspended')audioContext.resume();\n      const now=audioContext.currentTime,gain=audioContext.createGain(),a=audioContext.createOscillator(),b=audioContext.createOscillator();\n      a.type='sine';b.type='triangle';a.frequency.setValueAtTime(560,now);b.frequency.setValueAtTime(900,now);\n      gain.gain.setValueAtTime(.0001,now);gain.gain.exponentialRampToValueAtTime(.045,now+.008);gain.gain.exponentialRampToValueAtTime(.0001,now+.075);\n      a.connect(gain);b.connect(gain);gain.connect(audioContext.destination);a.start(now);b.start(now);a.stop(now+.08);b.stop(now+.08);\n    }catch(_){}\n  }'''
new = '''  function clickSound(){\n    try{\n      audioContext=audioContext||new(window.AudioContext||window.webkitAudioContext)();\n      if(audioContext.state==='suspended')audioContext.resume();\n      const now=audioContext.currentTime;\n      const master=audioContext.createGain();\n      master.gain.setValueAtTime(.0001,now);\n      master.gain.exponentialRampToValueAtTime(.055,now+.008);\n      master.gain.exponentialRampToValueAtTime(.0001,now+.13);\n      master.connect(audioContext.destination);\n      [[620,0,.08,'sine'],[880,.035,.095,'sine']].forEach(([freq,delay,duration,type])=>{\n        const osc=audioContext.createOscillator();\n        const gain=audioContext.createGain();\n        osc.type=type;\n        osc.frequency.setValueAtTime(freq,now+delay);\n        osc.frequency.exponentialRampToValueAtTime(freq*1.045,now+delay+duration);\n        gain.gain.setValueAtTime(.0001,now+delay);\n        gain.gain.exponentialRampToValueAtTime(.72,now+delay+.006);\n        gain.gain.exponentialRampToValueAtTime(.0001,now+delay+duration);\n        osc.connect(gain);gain.connect(master);\n        osc.start(now+delay);osc.stop(now+delay+duration+.01);\n      });\n    }catch(_){}\n  }'''
if old not in s:
    raise SystemExit('clickSound function not found')
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
