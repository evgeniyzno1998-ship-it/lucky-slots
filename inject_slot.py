import sys, re

with open('C:/Users/Kakashka PC/Downloads/НОВЫЙ ДИЗАЙН/Игра с анимацией.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract getSymbolSVG function
start_idx = text.find('function getSymbolSVG(type) {')
end_idx = text.find('}', text.find('case \'lollipop\':')) + 30 
svg_func = text[start_idx:text.find('}', end_idx) + 1]

new_logic = f"""
        /* === NEW RUBY SLOT GAME LOGIC === */
        const emojiToSvgMap = {{
            "🍒": "peach",
            "🍋": "star",
            "🍊": "lollipop",
            "🍇": "grape",
            "🍫": "diamond",
            "🍭": "apple",
            "🍬": "heart",
            "💎": "ruby",
            "🎰": "star",
            "💣": "diamond"
        }};
        const symbolTypes = ['ruby', 'grape', 'apple', 'peach', 'diamond', 'heart', 'star', 'lollipop'];

        {svg_func}

        var BET_STEPS = [1, 5, 10, 25, 50, 100, 200];
        var betIndex = 1;

        function initGame() {{
            var g = document.getElementById('slot-grid');
            if (g && !g.children.length) {{
                g.innerHTML = '';
                for(let i=0; i<30; i++) {{
                    const type = symbolTypes[Math.floor(Math.random() * symbolTypes.length)];
                    createTile(i, type);
                }}
            }}
            updateSpinBtn(); updateBetDisplay();
        }}

        function createTile(index, type, animateClass = '') {{
            const g = document.getElementById('slot-grid');
            const div = document.createElement('div');
            const col = index % 6;
            const delay = col * 50; 
            div.className = `symbol-tile ${{animateClass}}`;
            div.style.animationDelay = `${{delay}}ms`;
            div.innerHTML = getSymbolSVG(type);
            div.dataset.index = index;
            div.dataset.type = type;
            if(g) g.appendChild(div);
            return div;
        }}
        
        function updateBetDisplay() {{
            var bd = document.getElementById('betDisplay');
            if(bd) bd.textContent = bet.toFixed(2);
        }}

        function changeBet(dir) {{
            if (spinning) return;
            betIndex = BET_STEPS.indexOf(bet);
            if (betIndex === -1) betIndex = 0;
            betIndex += dir;
            if (betIndex < 0) betIndex = 0;
            if (betIndex >= BET_STEPS.length) betIndex = BET_STEPS.length - 1;
            bet = BET_STEPS[betIndex];
            updateBetDisplay(); updateSpinBtn();
        }}

        function setMaxBet() {{
            if (spinning) return;
            bet = BET_STEPS[BET_STEPS.length - 1];
            betIndex = BET_STEPS.length - 1;
            updateBetDisplay(); updateSpinBtn();
        }}

        function toggleAutoSpeed() {{
            speedMode = (speedMode + 1) % 3;
            var labels = ['🐢', '▶️', '⚡'];
            var al = document.getElementById('autoLabel');
            var icon = document.getElementById('turboIcon');
            if(al) al.textContent = labels[speedMode];
            if(icon) {{
                if(speedMode === 0) icon.textContent = 'speed';
                if(speedMode === 1) icon.textContent = 'play_arrow';
                if(speedMode === 2) icon.textContent = 'bolt';
            }}
        }}

        function updateSpinBtn() {{
            var btn = document.getElementById('spinBtn');
            if(btn) btn.disabled = (balance === null);
        }}

        function triggerSparkles(x, y) {{
            for(let i=0; i<8; i++) {{
                const sparkle = document.createElement('div');
                sparkle.className = 'sparkle';
                sparkle.style.left = x + 'px';
                sparkle.style.top = y + 'px';
                const angle = Math.random() * Math.PI * 2;
                const distance = 30 + Math.random() * 50;
                sparkle.style.setProperty('--tx', Math.cos(angle) * distance + 'px');
                sparkle.style.setProperty('--ty', Math.sin(angle) * distance + 'px');
                document.body.appendChild(sparkle);
                setTimeout(() => sparkle.remove(), 1000);
            }}
        }}

        function showBigWin(amount) {{
            var bwOverlay = document.getElementById('big-win-overlay');
            var bwAmount = document.getElementById('win-counter-big');
            if(bwOverlay) bwOverlay.style.display = 'flex';
            if(bwAmount) bwAmount.innerText = amount;
            
            const colors = ['#FFD700', '#C0142A', '#FFFFFF'];
            const container = document.getElementById('confetti-box');
            if(container) {{
                container.innerHTML = ''; 
                for(let i=0; i<50; i++) {{
                    const conf = document.createElement('div');
                    conf.style.position = 'absolute';
                    conf.style.width = '8px';
                    conf.style.height = '16px';
                    conf.style.background = colors[Math.floor(Math.random() * colors.length)];
                    conf.style.left = Math.random() * 100 + '%';
                    conf.style.top = -20 + 'px';
                    conf.style.transform = `rotate(${{Math.random() * 360}}deg)`;
                    conf.animate([
                        {{ transform: `translateY(0) rotate(0deg)`, opacity: 1 }},
                        {{ transform: `translateY(100vh) rotate(${{720 + Math.random()*360}}deg)`, opacity: 0 }}
                    ], {{
                        duration: 1000 + Math.random() * 1000,
                        easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
                        fill: 'forwards'
                    }});
                    container.appendChild(conf);
                }}
            }}
        }}
        
        function closeBigWin() {{
            var bwOverlay = document.getElementById('big-win-overlay');
            if(bwOverlay) bwOverlay.style.display = 'none';
        }}

        function doSpin() {{
            if (balance === null) return;
            if ((balance < bet && freeSpins <= 0) && activeWallet !== 'stars') {{ nav('wallet'); return }}
            if ((activeWallet === 'stars' && starsBalance < bet && freeSpins <= 0)) {{ selectPayMethod('stars'); nav('wallet'); return; }}
            spin();
        }}

        async function spin() {{
            if(spinning) return; 
            spinning = true; 
            var btn = document.getElementById('spinBtn'); 
            if(btn) btn.disabled = true;
            if(btn) btn.style.transform = 'scale(0.9)';
            setTimeout(() => {{ if(btn) btn.style.transform = 'scale(1)' }}, 150);
            
            var wd = document.getElementById('win-display');
            var badge = document.getElementById('tumble-badge');
            var g = document.getElementById('slot-grid');
            if(wd) {{ wd.innerText = '0.00'; wd.classList.remove('text-[#FFD700]', 'scale-110'); wd.classList.add('text-white'); }}
            if(badge) {{ badge.classList.remove('scale-100', 'opacity-100'); badge.classList.add('scale-0', 'opacity-0'); }}
            
            var tiles = Array.from(g.children);
            tiles.forEach((tile, i) => {{
                const col = i % 6;
                setTimeout(() => {{
                    tile.classList.add('spinning-column');
                }}, col * 60);
            }});

            const SPIN_BASE = speedMode === 2 ? 300 : 700;
            const COL_STAGGER = speedMode === 2 ? 40 : 90;
            
            try {{
                var useFree = freeSpins > 0 && ((activeWallet === 'usdt' && balance < bet) || (activeWallet === 'stars' && starsBalance < bet));
                var r = await fetch(API + '/api/spin', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(Object.assign({{}}, auth(), {{ bet: bet, use_free_spin: useFree, wallet: activeWallet }})) }});
                var d = await r.json(); 
                
                if (!d.ok) {{ 
                    spinning = false; 
                    if(btn) btn.disabled = false; 
                    if (d.balance !== undefined) balance = d.balance; 
                    if (d.stars !== undefined) starsBalance = d.stars;
                    updateBalanceUI(); 
                    tiles.forEach(t => t.classList.remove('spinning-column'));
                    return;
                }}
                
                if (d.balance !== undefined) balance = d.balance; 
                if (d.stars !== undefined) starsBalance = d.stars;
                freeSpins = d.free_spins || freeSpins;
                updateBalanceUI();

                var newTypes = d.grid.map(emoji => emojiToSvgMap[emoji] || 'ruby');

                setTimeout(() => {{
                    g.innerHTML = '';
                    const newTiles = [];
                    for (let i = 0; i < 30; i++) {{
                        const div = document.createElement('div');
                        div.className = 'symbol-tile';
                        div.style.opacity = '0';
                        div.style.transform = 'translateY(-110%) scaleY(1.15)';
                        div.dataset.type = newTypes[i];
                        div.dataset.index = i;
                        div.innerHTML = getSymbolSVG(newTypes[i]);
                        g.appendChild(div);
                        newTiles.push(div);
                    }}

                    for (let col = 0; col < 6; col++) {{
                        const colDelay = col * COL_STAGGER;
                        setTimeout(() => {{
                            for (let row = 0; row < 5; row++) {{
                                const tile = newTiles[row * 6 + col];
                                const rowDelay = row * 35; 
                                setTimeout(() => {{
                                    tile.style.opacity = '1';
                                    tile.style.transform = '';
                                    void tile.offsetWidth;
                                    tile.classList.add('reel-land');
                                }}, rowDelay);
                            }}
                        }}, colDelay);
                    }}

                    const totalAnim = (5) * COL_STAGGER + (4) * 35 + 520;
                    setTimeout(() => {{
                        if(d.winnings > 0) {{
                            var co = {{}}; d.grid.forEach(function (s) {{ if (s !== '🎰') co[s] = (co[s] || 0) + 1 }});
                            var ws = new Set(Object.entries(co).filter(function (e) {{ return e[1] >= 8 }}).map(function (e) {{ return emojiToSvgMap[e[0]] || 'ruby' }}));
                            
                            newTiles.forEach(t => {{
                                if(ws.has(t.dataset.type)) {{
                                    t.classList.add('winning-tile');
                                    const rect = t.getBoundingClientRect();
                                    triggerSparkles(rect.left + rect.width/2, rect.top + rect.height/2);
                                }} else {{
                                    t.style.opacity = '0.3';
                                }}
                            }});
                            
                            animateValue(wd, 0, parseFloat(d.winnings), 1000);
                            wd.classList.remove('text-white');
                            wd.classList.add('text-[#FFD700]');
                            if(badge) {{
                                badge.classList.remove('scale-0', 'opacity-0');
                                badge.classList.add('scale-100', 'opacity-100');
                            }}
                            if(d.winnings > bet * 5) {{
                                setTimeout(() => showBigWin(d.winnings.toFixed(2)), 500);
                            }}
                        }}

                        if (d.triggered_bonus) {{
                            setTimeout(function () {{ startBonus('triggered') }}, 1200);
                        }}

                        spinning = false; 
                        if(btn) btn.disabled = false;
                    }}, totalAnim);

                }}, Math.max(0, SPIN_BASE - 500)); 

            }} catch (e) {{ 
                spinning = false; 
                if(btn) btn.disabled = false;
                tiles.forEach(t => t.classList.remove('spinning-column'));
            }}
        }}

        function animateValue(obj, start, end, duration) {{
            let startTimestamp = null;
            const step = (timestamp) => {{
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                obj.innerHTML = (progress * (end - start) + start).toFixed(2);
                if (progress < 1) {{
                    window.requestAnimationFrame(step);
                }}
            }};
            window.requestAnimationFrame(step);
        }}
"""

with open('C:/Users/Kakashka PC/Downloads/КОПИЯ БОТА ДЛЯ ГРАВИТИГУГЛ/index.html', 'r', encoding='utf-8') as f:
    orig = f.read()

tgt_start = orig.find('/* === GAME === */')
tgt_end = orig.find('/* === BONUS === */', tgt_start)

if tgt_start != -1 and tgt_end != -1:
    orig = orig[:tgt_start] + new_logic + '\n        ' + orig[tgt_end:]
    with open('C:/Users/Kakashka PC/Downloads/КОПИЯ БОТА ДЛЯ ГРАВИТИГУГЛ/index.html', 'w', encoding='utf-8') as f:
        f.write(orig)
    print("SUCCESS")
else:
    print("FAILURE")
