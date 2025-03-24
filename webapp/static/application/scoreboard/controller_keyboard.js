const KEYBINDS = {
    /* Main Time and Misc */
    " ": () => { if (sbState.time.running) { stop_time.click() } else { start_time.click() } },
    ".": () => { flash_medical.click() },
    /* Views */
    "1": () => { main_view.click() },
    "2": () => { callup_view.click() },
    "3": () => { break_view.click() },
    /* Osaekomi */
    "c": () => { white_start_osaekomi.click() },
    "C": () => { white_stop_osaekomi.click() },
    "m": () => { blue_start_osaekomi.click() },
    "M": () => { blue_stop_osaekomi.click() },
    "b": () => { toggle_osaekomi.click() },
}

INSIDE_OUT_LIST = [
    ['q', 'Q', 'ü', 'Ü'],
    ['w', 'W', 'p', 'P'],
    ['e', 'E', 'o', 'O'],
    ['r', 'R', 'i', 'I'],
    ['t', 'T', 'u', 'U']
]

{
    let i = 0;
    for (const side of sides) {
        let j = 0;
        for (const score_name of SBRULES.controls) {
            if (score_name != 'osaekomi') {
                let up_elem = document.querySelector(
                    "[data-control='" + side + ".expand'][data-score='" + score_name + "']")
                let down_elem = document.querySelector(
                    "[data-control='" + side + ".reduce'][data-score='" + score_name + "']")
                
                if (j >= INSIDE_OUT_LIST.length) break;

                KEYBINDS[INSIDE_OUT_LIST[j][i]] = (() => { up_elem.click() })
                KEYBINDS[INSIDE_OUT_LIST[j][i + 1]] = (() => { down_elem.click() })
                j++;
            }
        }
        i += 2;
    }
}

var KEYBIND_OVERRIDES = KEYBIND_OVERRIDES || {};


window.addEventListener("keypress", (e) => {
    if(e.target.tagName == "INPUT") {
        return
    }

    let keycode = (e.ctrlKey ? "Ctrl-" : "") + (e.altKey ? "Alt-" : "") + e.key

    if(typeof KEYBIND_OVERRIDES != undefined) {
        if (KEYBIND_OVERRIDES[keycode]) {
            keycode = KEYBIND_OVERRIDES[keycode]
        }
    }

    if (KEYBINDS[keycode]) {
        KEYBINDS[keycode]()
        e.preventDefault()
        return true
    }
})