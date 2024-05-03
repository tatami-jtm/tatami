/* ************ *
 * Declarations *
 * ************ */

var sbState

const mat_number = document.querySelector("[data-static=\"mat-number\"]").innerText
const current_screen = document.getElementById("current-screen")
const global_time = document.getElementById("global-time")
const white_osaekomi = document.getElementById("osaekomi-white")
const blue_osaekomi = document.getElementById("osaekomi-blue")

const main_view = document.querySelector("[data-control=\"view.main\"]")
const callup_view = document.querySelector("[data-control=\"view.callup\"]")
const break_view = document.querySelector("[data-control=\"view.break\"]")

const start_time = document.querySelector("[data-control=\"time.main.start\"]")
const stop_time = document.querySelector("[data-control=\"time.main.stop\"]")
const correct_time = document.querySelector("[data-control=\"time.main.correct\"]")
const flash_medical = document.querySelector("[data-control=\"flash.medical\"]")

const toggle_osaekomi = document.querySelector("[data-control=\"osaekomi.toggle\"]")

const white_start_osaekomi = document.querySelector("[data-control=\"osaekomi.white.start\"]")
const white_stop_osaekomi = document.querySelector("[data-control=\"osaekomi.white.stop\"]")
const blue_start_osaekomi = document.querySelector("[data-control=\"osaekomi.blue.start\"]")
const blue_stop_osaekomi = document.querySelector("[data-control=\"osaekomi.blue.stop\"]")

const ippon_white = document.getElementById("ippon-white")
const ippon_blue = document.getElementById("ippon-blue")
const white_expand_ippon = document.querySelector("[data-control=\"ippon.white.expand\"]")
const white_reduce_ippon = document.querySelector("[data-control=\"ippon.white.reduce\"]")
const blue_expand_ippon = document.querySelector("[data-control=\"ippon.blue.expand\"]")
const blue_reduce_ippon = document.querySelector("[data-control=\"ippon.blue.reduce\"]")

const wazaari_white = document.getElementById("wazaari-white")
const wazaari_blue = document.getElementById("wazaari-blue")
const white_expand_wazaari = document.querySelector("[data-control=\"wazaari.white.expand\"]")
const white_reduce_wazaari = document.querySelector("[data-control=\"wazaari.white.reduce\"]")
const blue_expand_wazaari = document.querySelector("[data-control=\"wazaari.blue.expand\"]")
const blue_reduce_wazaari = document.querySelector("[data-control=\"wazaari.blue.reduce\"]")

const shido_white = document.getElementById("shido-white")
const shido_blue = document.getElementById("shido-blue")
const white_expand_shido = document.querySelector("[data-control=\"shido.white.expand\"]")
const white_reduce_shido = document.querySelector("[data-control=\"shido.white.reduce\"]")
const blue_expand_shido = document.querySelector("[data-control=\"shido.blue.expand\"]")
const blue_reduce_shido = document.querySelector("[data-control=\"shido.blue.reduce\"]")

const hansokumake_white = document.getElementById("hansokumake-white")
const hansokumake_blue = document.getElementById("hansokumake-blue")
const white_expand_hansokumake = document.querySelector("[data-control=\"hansokumake.white.expand\"]")
const white_reduce_hansokumake = document.querySelector("[data-control=\"hansokumake.white.reduce\"]")
const blue_expand_hansokumake = document.querySelector("[data-control=\"hansokumake.blue.expand\"]")
const blue_reduce_hansokumake = document.querySelector("[data-control=\"hansokumake.blue.reduce\"]")


/* *********** *
 * Controllers *
 * *********** */


/* Main load */
window.addEventListener("load", () => {
    setOption("reset", true)
    sbState = makeState(local_config || {
        fightDuration: 240,
        hasGoldenScore: true,
        maxGoldenScore: null,
        defaultScreen: 'main'
    });

    setInterval(tick, 50)
    setInterval(renderControls, 100)
    setInterval(renderBoard, 100)
})

/* Control: Main Time */
start_time.addEventListener("click", () => {
    sbState.time.running = true
})
stop_time.addEventListener("click", () => {
    sbState.time.running = false
})

correct_time.addEventListener("click", () => {
    let current_time = new Date(properIntegralConversion(sbState.time.displayTime / 1000) * 1000).toISOString().substr(15, 4)

    if (sbState.time.goldenScore)
        current_time = current_time + "G"

    let new_time = prompt("Auf welchen Wert soll die Zeit korrigiert werden?\nDie Zeit muss in dem Format 'm:ss' angegeben werden.\n'G' am Ende hinzufügen für Golden Score", current_time)
    if (new_time == null) return

    if (new_time.endsWith('G')) {
        sbState.time.goldenScore = true
        sbState.time.displayTimeDirection = 1

        new_time = new_time.trimEnd('G')
    } else {
        sbState.time.displayTimeDirection = -1
    }

    new_time = new_time.split(":")
    if (new_time.length != 2) return

    new_time = (parseInt(new_time[0])*60 + parseInt(new_time[1])) * 1000
    sbState.time.displayTime = new_time;
})

/* Control: Views */
main_view.addEventListener("click", () => {
    sbState.view.screen = 'main'
})
callup_view.addEventListener("click", () => {
    sbState.view.screen = 'callup'
})
break_view.addEventListener("click", () => {
    sbState.view.screen = 'break'
})

/* Control: Medical Alert */
flash_medical.addEventListener("click", () => {
    sbState.view.medical = !sbState.view.medical
})

/* Control: Osaekomi */
white_start_osaekomi.addEventListener("click", () => {
    sbState.white.osaekomi.running = true
    sbState.white.osaekomi.since = sbState.time.globalTick
    sbState.white.osaekomi.wazaari_given = false
    sbState.blue.osaekomi.running = false
})
white_stop_osaekomi.addEventListener("click", () => {
    sbState.white.osaekomi.running = false
})

blue_start_osaekomi.addEventListener("click", () => {
    sbState.blue.osaekomi.running = true
    sbState.blue.osaekomi.since = sbState.time.globalTick
    sbState.blue.osaekomi.wazaari_given = false
    sbState.white.osaekomi.running = false
})
blue_stop_osaekomi.addEventListener("click", () => {
    sbState.blue.osaekomi.running = false
})

toggle_osaekomi.addEventListener("click", () => {
    if(sbState.blue.osaekomi.running) {
        sbState.blue.osaekomi.running = false
        sbState.white.osaekomi.running = true
        sbState.white.osaekomi.since = sbState.blue.osaekomi.since
        sbState.white.osaekomi.wazaari_given = false
        if (sbState.blue.osaekomi.wazaari_given)
            sbState.blue.wazaari_pending = false;
    } else if(sbState.white.osaekomi.running) {
        sbState.white.osaekomi.running = false
        sbState.blue.osaekomi.running = true
        sbState.blue.osaekomi.since = sbState.white.osaekomi.since
        sbState.blue.osaekomi.wazaari_given = false
        if (sbState.white.osaekomi.wazaari_given)
            sbState.white.wazaari_pending = false;
    }
})

/* Control: Ippon */

white_expand_ippon.addEventListener("click", () => {
    sbState.white.ippon = true
    sbState.time.running = false
})

white_reduce_ippon.addEventListener("click", () => {
    sbState.white.ippon = false
})

blue_expand_ippon.addEventListener("click", () => {
    sbState.blue.ippon = true
    sbState.time.running = false
})

blue_reduce_ippon.addEventListener("click", () => {
    sbState.blue.ippon = false
})

/* Control: Wazaari */

white_expand_wazaari.addEventListener("click", () => {
    if (sbState.white.wazaari)
        sbState.white.wazaari_awasete_ippon = true
    else
        sbState.white.wazaari = true

    sbState.white.wazaari_pending = false

    if (sbState.time.goldenScore || sbState.white.wazaari_awasete_ippon) {
        sbState.time.running = false
    }
})

white_reduce_wazaari.addEventListener("click", () => {
    if (sbState.white.wazaari_awasete_ippon)
        sbState.white.wazaari_awasete_ippon = false
    else
        sbState.white.wazaari = false

    sbState.white.wazaari_pending = false
})

blue_expand_wazaari.addEventListener("click", () => {
    if (sbState.blue.wazaari)
        sbState.blue.wazaari_awasete_ippon = true
    else
        sbState.blue.wazaari = true

    sbState.blue.wazaari_pending = false

    if (sbState.time.goldenScore || sbState.blue.wazaari_awasete_ippon) {
        sbState.time.running = false
    }
})

blue_reduce_wazaari.addEventListener("click", () => {
    if (sbState.blue.wazaari_awasete_ippon)
        sbState.blue.wazaari_awasete_ippon = false
    else
        sbState.blue.wazaari = false

    sbState.blue.wazaari_pending = false
})

/* Control: Shido */

white_expand_shido.addEventListener("click", () => {
    if (sbState.white.shido < 3)
        sbState.white.shido += 1
})

white_reduce_shido.addEventListener("click", () => {
    if (sbState.white.shido > 0)
        sbState.white.shido -= 1
})

blue_expand_shido.addEventListener("click", () => {
    if (sbState.blue.shido < 3)
        sbState.blue.shido += 1
})

blue_reduce_shido.addEventListener("click", () => {
    if (sbState.blue.shido > 0)
        sbState.blue.shido -= 1
})

/* Control: Hansoku-Make */

white_expand_hansokumake.addEventListener("click", () => {
    sbState.white.hansokumake = true
    sbState.time.running = false
})

white_reduce_hansokumake.addEventListener("click", () => {
    sbState.white.hansokumake = false
})

blue_expand_hansokumake.addEventListener("click", () => {
    sbState.blue.hansokumake = true
    sbState.time.running = false
})

blue_reduce_hansokumake.addEventListener("click", () => {
    sbState.blue.hansokumake = false
})