from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
start=s.find('    const CATEGORY_RULES=[')
if start<0: raise SystemExit('CATEGORY_RULES start not found')
end=s.find('    ];',start)
if end<0: raise SystemExit('CATEGORY_RULES end not found')
end += len('    ];')
new='''    const CATEGORY_RULES=[\n      ['Action',['action','shooter','combat','battle','fight','war','zombie','ninja','stickman','assassin','gun','sniper','strike','rush','arena','brawler','fighter','hero']],\n      ['Adventure',['adventure','quest','platform','dungeon','maze','escape','explore','survival','island','parkour','treasure','mystery']],\n      ['Arcade',['arcade','flappy','runner','run','jump','brick','ball','bubble','match','pinball','snake','pong','breakout','stack','tap']],\n      ['Puzzle',['puzzle','logic','sudoku','2048','mahjong','word','memory','connect','block','brain','sort','merge','numbers','crossword','jigsaw']],\n      ['Racing',['racing','race','drift','car','cars','motor','bike','bmx','kart','traffic','drive','rally','formula','truck','rider']],\n      ['Sports',['football','soccer','basketball','baseball','golf','tennis','hockey','volleyball','bowling','pool','sports','skate','ski','boxing','wrestling','cricket']],\n      ['Strategy',['strategy','tower','defense','defence','battle','td','idle','tycoon','manager','kingdom','chess','checkers','warcraft','empire','tactics']],\n      ['Simulation',['simulator','simulation','farming','farm','restaurant','cooking','shop','business','city','hotel','airport','life','house','doctor','hospital','school','job']],\n      ['Multiplayer',['multiplayer','2 player','2p','io','agar','slither','online','versus','vs','co-op','coop']],\n      ['Casual',['clicker','idle','dress','makeup','color','drawing','quiz','trivia','fun','cute','music','piano','matching','decorate']]\n    ];'''
s=s[:start]+new+s[end:]
# Make the automatic system always rebuild category counts after games load/change.
anchor="    function render(){\n      const gs=games();"
if anchor not in s: raise SystemExit('category render anchor not found')
# Add a small status subtitle and icons without requiring per-game edits.
s=s.replace(anchor,"    function render(){\n      const gs=games();",1)
# Strengthen the categorization fallback and scoring so existing and future games are handled consistently.
old="""    function categoryFor(title){\n      const text=normalize(title);\n      let best='Casual',bestScore=0;\n      CATEGORY_RULES.forEach(([name,words])=>{\n        const score=words.reduce((n,w)=>n+(text.includes(normalize(w))?1:0),0);\n        if(score>bestScore){best=name;bestScore=score;}\n      });\n      return best;\n    }"""
newcat="""    function categoryFor(title){\n      const text=normalize(title);\n      let best='Casual',bestScore=0;\n      CATEGORY_RULES.forEach(([name,words])=>{\n        let score=0;\n        words.forEach(word=>{\n          const w=normalize(word);\n          if(!w)return;\n          if(text===w)score+=4;\n          else if((` ${text} `).includes(` ${w} `))score+=3;\n          else if(text.includes(w))score+=1;\n        });\n        if(score>bestScore){best=name;bestScore=score;}\n      });\n      return best;\n    }"""
if oldcat in s: s=s.replace(oldcat,newcat,1)
# Ensure dynamic imports/new games cause immediate recategorization and preserve current selection.
oldobs="""    const observer=new MutationObserver(()=>render());\n    observer.observe(grid,{childList:true});\n    render();"""
newobs="""    const observer=new MutationObserver(()=>{render();});\n    observer.observe(grid,{childList:true});\n    window.addEventListener('load',()=>render());\n    render();"""
if oldobs in s: s=s.replace(oldobs,newobs,1)
p.write_text(s,encoding='utf-8')
