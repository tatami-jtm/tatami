/* ************ *
 * Declarations *
 * ************ */

var sbState

const mat_number = document.querySelector("[data-static=\"mat-number\"]").innerText
const global_time = document.getElementById("global-time")
const white_osaekomi = document.getElementById("osaekomi-white")
const blue_osaekomi = document.getElementById("osaekomi-blue")

const main_view = document.querySelector("[data-control=\"view.main\"]")
const callup_view = document.querySelector("[data-control=\"view.callup\"]")
const break_view = document.querySelector("[data-control=\"view.break\"]")

const start_time = document.querySelector("[data-control=\"time.main.start\"]")
const stop_time = document.querySelector("[data-control=\"time.main.stop\"]")
const flash_medical = document.querySelector("[data-control=\"flash.medical\"]")

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

const white_expand_shido = document.querySelector("[data-control=\"shido.white.expand\"]")
const white_reduce_shido = document.querySelector("[data-control=\"shido.white.reduce\"]")
const blue_expand_shido = document.querySelector("[data-control=\"shido.blue.expand\"]")
const blue_reduce_shido = document.querySelector("[data-control=\"shido.blue.reduce\"]")

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
    sbState = makeState({ fightDuration: 240, hasGoldenScore: true });

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
})
white_stop_osaekomi.addEventListener("click", () => {
    sbState.white.osaekomi.running = false
})

blue_start_osaekomi.addEventListener("click", () => {
    sbState.blue.osaekomi.running = true
    sbState.blue.osaekomi.since = sbState.time.globalTick
})
blue_stop_osaekomi.addEventListener("click", () => {
    sbState.blue.osaekomi.running = false
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
    sbState.white.wazaari = true
    sbState.white.wazaari_pending = false
})

white_reduce_wazaari.addEventListener("click", () => {
    sbState.white.wazaari = false
    sbState.white.wazaari_pending = false
})

blue_expand_wazaari.addEventListener("click", () => {
    sbState.blue.wazaari = true
    sbState.blue.wazaari_pending = false
})

blue_reduce_wazaari.addEventListener("click", () => {
    sbState.blue.wazaari = false
    sbState.blue.wazaari_pending = false
})