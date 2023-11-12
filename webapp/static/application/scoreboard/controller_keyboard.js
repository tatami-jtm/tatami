const KEYBINDS = {
    /* Main Time and Misc */
    " ": () => { if (sbState.time.running) { stop_time.click() } else { start_time.click() } },
    ".": () => { flash_medical.click() },
    "Enter": () => { transactional_end_fight.click() },
    /* Views */
    "1": () => { main_view.click() },
    "2": () => { callup_view.click() },
    "3": () => { break_view.click() },
    /* White Scores and Penalties */
    "q": () => { white_expand_ippon.click() },
    "Q": () => { white_reduce_ippon.click() },
    "w": () => { white_expand_wazaari.click() },
    "W": () => { white_reduce_wazaari.click() },
    "e": () => { white_expand_shido.click() },
    "E": () => { white_reduce_shido.click() },
    "r": () => { white_expand_hansokumake.click() },
    "R": () => { white_reduce_hansokumake.click() },
    /* Blue Scores and Penalties */
    "ü": () => { blue_expand_ippon.click() },
    "Ü": () => { blue_reduce_ippon.click() },
    "p": () => { blue_expand_wazaari.click() },
    "P": () => { blue_reduce_wazaari.click() },
    "o": () => { blue_expand_shido.click() },
    "O": () => { blue_reduce_shido.click() },
    "i": () => { blue_expand_hansokumake.click() },
    "I": () => { blue_reduce_hansokumake.click() },
    /* Osaekomi */
    "c": () => { white_start_osaekomi.click() },
    "C": () => { white_stop_osaekomi.click() },
    "m": () => { blue_start_osaekomi.click() },
    "M": () => { blue_stop_osaekomi.click() },
    "b": () => { toggle_osaekomi.click() },
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