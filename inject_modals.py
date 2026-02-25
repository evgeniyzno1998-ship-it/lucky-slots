import sys

modal_logic = """
        /* === NEW SLOTS MODALS & AUTOSPIN === */
        function togglePaytable(show) {
            const modal = document.getElementById('paytable-modal');
            if (!modal) return;
            if(show) {
                modal.style.opacity = '1';
                modal.style.pointerEvents = 'auto';
            } else {
                modal.style.opacity = '0';
                modal.style.pointerEvents = 'none';
            }
        }

        let isAutoSpinning = false;
        let autoSpinsLeft = 0;
        let selectedAutoAmount = 25;

        function openAutoModal() {
            if(spinning || isAutoSpinning) return;
            selectedAutoAmount = 25;
            updateAutoChips();
            const modal = document.getElementById('autospin-modal');
            if(modal) {
                modal.style.opacity = '1';
                modal.style.pointerEvents = 'auto';
            }
        }

        function toggleAutoModal(show) {
            const modal = document.getElementById('autospin-modal');
            if (!modal) return;
            modal.style.opacity = show ? '1' : '0';
            modal.style.pointerEvents = show ? 'auto' : 'none';
        }

        function selectAutoChip(btn, amount) {
            selectedAutoAmount = amount;
            updateAutoChips();
        }

        function updateAutoChips() {
            const btns = document.querySelectorAll('#autoSpinsGrid .option-chip');
            if(!btns.length) return;
            btns.forEach(b => b.classList.remove('selected'));
            const map = {10:0, 25:1, 50:2, 100:3, 9999:4};
            if(map[selectedAutoAmount] !== undefined && btns[map[selectedAutoAmount]]) {
                btns[map[selectedAutoAmount]].classList.add('selected');
            }
        }

        function startAutoSpinFlow() {
            autoSpinsLeft = selectedAutoAmount;
            isAutoSpinning = true;
            toggleAutoModal(false);
            
            var al = document.getElementById('autoLabel');
            if(al) al.textContent = 'STOP';
            var icon = document.getElementById('turboIcon');
            if(icon) icon.textContent = 'stop';
            
            doAutoSpin();
        }

        function stopAutoSpinFlow() {
            isAutoSpinning = false;
            autoSpinsLeft = 0;
            
            var labels = ['🐢', '▶️', '⚡'];
            var al = document.getElementById('autoLabel');
            if(al) al.textContent = labels[speedMode];
            var icon = document.getElementById('turboIcon');
            if(icon) {
                if(speedMode === 0) icon.textContent = 'speed';
                if(speedMode === 1) icon.textContent = 'play_arrow';
                if(speedMode === 2) icon.textContent = 'bolt';
            }
        }

        // Intercept Auto button depending on state
        function handleAutoBtnClick() {
            if(isAutoSpinning) {
                stopAutoSpinFlow();
            } else {
                openAutoModal();
            }
        }

        function doAutoSpin() {
            if(!isAutoSpinning || autoSpinsLeft <= 0) {
                stopAutoSpinFlow();
                return;
            }
            if(!spinning) {
                autoSpinsLeft--;
                doSpin(); 
                const checkInterval = setInterval(() => {
                    if(!spinning) {
                        clearInterval(checkInterval);
                        setTimeout(doAutoSpin, speedMode === 2 ? 200 : 700);
                    }
                }, 100);
            }
        }
"""

with open('C:/Users/Kakashka PC/Downloads/КОПИЯ БОТА ДЛЯ ГРАВИТИГУГЛ/index.html', 'r', encoding='utf-8') as f:
    orig = f.read()

# I will replace `function toggleAutoSpeed()` with the new `handleAutoBtnClick()` inside the HTML for the auto button, or I will just append the logic.
# Wait, let's append it right after `window.requestAnimationFrame(step);` \n        }
insert_idx = orig.find('window.requestAnimationFrame(step);\n        }') + 44

if insert_idx != 43:
    orig = orig[:insert_idx] + modal_logic + orig[insert_idx:]
    with open('C:/Users/Kakashka PC/Downloads/КОПИЯ БОТА ДЛЯ ГРАВИТИГУГЛ/index.html', 'w', encoding='utf-8') as f:
        f.write(orig)
    print("SUCCESS")
else:
    print("FAILURE")
