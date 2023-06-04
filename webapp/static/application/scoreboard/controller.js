const timeDefault = 10

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

const white_expand_ippon = document.querySelector("[data-control=\"ippon.white.expand\"]")
const white_reduce_ippon = document.querySelector("[data-control=\"ippon.white.reduce\"]")
const blue_expand_ippon = document.querySelector("[data-control=\"ippon.blue.expand\"]")
const blue_reduce_ippon = document.querySelector("[data-control=\"ippon.blue.reduce\"]")

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


var timeops = {
    globalTime: 0,
    tickOnlyTime: 0,
    ticking: 0,
    lastTick: null,
    goldenScore: false,
    view: 'break',
    medical: false,

    white: {
        osaekomi: false,
        osaekomiSince: null,
        ippon: false,
        wazaari: 0,
        shido: 0,
        hansokumake: false
    },

    blue: {
        osaekomi: false,
        osaekomiSince: null,
        ippon: false,
        wazaari: 0,
        shido: 0,
        hansokumake: false
    }
}

var globalTime, ticking


const initTime = () => {
    timeops.globalTime = timeDefault * 1000
    timeops.ticking = false
    updateTime()
}
const updateTime = () => {
    setOption("time:main", Math.ceil(timeops.globalTime / 1000))
    setOption("time:running", timeops.ticking)
    document.getElementById("global-time").innerText = new Date(Math.ceil(timeops.globalTime / 1000) * 1000).toISOString().substr(15, 4)

    if (timeops.goldenScore) {
        document.getElementById("global-time").classList.add("text-bg-warning")
        setOption("time:golden-score", "true")
    } else {
        document.getElementById("global-time").classList.remove("text-bg-warning")
        setOption("time:golden-score", "false")
    }
    
    if (timeops.white.osaekomi) {
        let osaekomi_time = Math.floor((timeops.white.osaekomiSince - timeops.globalTime) / 1000)
        setOption("time:osaekomi:white", osaekomi_time)
        document.getElementById("osaekomi-white").innerText = osaekomi_time

        if (osaekomi_time >= 20) {
            whiteExpandIppon()
            whiteStopOsaekomi()
            endTime()
        } else if (osaekomi_time >= 10) {
            if (timeops.white.wazaari == 'active') {
                whiteExpandIppon()
                whiteStopOsaekomi()
                endTime()
            } else if (timeops.white.wazaari != 'pending') {
                whiteUnclearWazaari()
            }
        }
    } else {
        setOption("time:osaekomi:white", -1)
        document.getElementById("osaekomi-white").innerText = "---"
    }

    if (timeops.blue.osaekomi) {
        let osaekomi_time = Math.floor((timeops.blue.osaekomiSince - timeops.globalTime) / 1000)
        setOption("time:osaekomi:blue", osaekomi_time)
        document.getElementById("osaekomi-blue").innerText = osaekomi_time
    } else {
        setOption("time:osaekomi:blue", -1)
        document.getElementById("osaekomi-blue").innerText = "---"
    }
}
const mainView = () => {
    timeops.view = 'main'
    setOption("view", "main")

    main_view.classList.add("active")
    callup_view.classList.remove("active")
    break_view.classList.remove("active")
}
const callupView = () => {
    timeops.view = 'callup'
    setOption("view", "callup")

    main_view.classList.remove("active")
    callup_view.classList.add("active")
    break_view.classList.remove("active")
}
const breakView = () => {
    timeops.view = 'break'
    setOption("view", "break")

    main_view.classList.remove("active")
    callup_view.classList.remove("active")
    break_view.classList.add("active")
}
const startTime = () => {
    timeops.ticking = true

    disable_btn(start_time, "btn-success")
    enable_btn(stop_time, "btn-danger")
}
const stopTime = () => {
    timeops.ticking = false

    disable_btn(stop_time, "btn-danger")
    enable_btn(start_time, "btn-success")
}
const endTime = () => {
    stopTime()
    if (timeops.globalTime <= 0)
        timeops.globalTime = 0
    setOption("time:flash-alert", true)
    setTimeout(() => {
        setOption("time:flash-alert", false)
    }, 3000)
}
const flashMedical = () => {
    timeops.medical = !timeops.medical

    if (timeops.medical) {
        setOption("time:flash-medical", true)
        flash_medical.classList.add("active")
    } else  {
        setOption("time:flash-medical", false)
        flash_medical.classList.remove("active")
    }
}
const whiteStartOsaekomi = () => {
    timeops.white.osaekomi = true
    timeops.white.osaekomiSince = timeops.globalTime

    disable_btn(white_start_osaekomi, "btn-secondary")
    enable_btn(white_stop_osaekomi, "btn-secondary")
}
const whiteStopOsaekomi = () => {
    timeops.white.osaekomi = false
    timeops.white.osaekomiSince = null

    disable_btn(white_stop_osaekomi, "btn-secondary")
    enable_btn(white_start_osaekomi, "btn-secondary")
}
const blueStartOsaekomi = () => {
    timeops.blue.osaekomi = true
    timeops.blue.osaekomiSince = timeops.globalTime

    disable_btn(blue_start_osaekomi, "btn-secondary")
    enable_btn(blue_stop_osaekomi, "btn-secondary")
}
const blueStopOsaekomi = () => {
    timeops.blue.osaekomi = false
    timeops.blue.osaekomiSince = null

    disable_btn(blue_stop_osaekomi, "btn-secondary")
    enable_btn(blue_start_osaekomi, "btn-secondary")
}

const whiteExpandIppon = () => {
    timeops.white.ippon = true
    setOption("white:ippon", 1)
    document.getElementById("ippon-white").innerText = "1"

    disable_btn(white_expand_ippon, "btn-secondary")
    enable_btn(white_reduce_ippon, "btn-secondary")
}
const whiteReduceIppon = () => {
    timeops.white.ippon = false
    setOption("white:ippon", 0)
    document.getElementById("ippon-white").innerText = "0"

    disable_btn(white_reduce_ippon, "btn-secondary")
    enable_btn(white_expand_ippon, "btn-secondary")
}

const blueExpandIppon = () => {
    timeops.blue.ippon = true
    setOption("blue:ippon", 1)
    document.getElementById("ippon-blue").innerText = "1"

    disable_btn(blue_expand_ippon, "btn-secondary")
    enable_btn(blue_reduce_ippon, "btn-secondary")
}
const blueReduceIppon = () => {
    timeops.blue.ippon = false
    setOption("blue:ippon", 0)
    document.getElementById("ippon-blue").innerText = "0"

    disable_btn(blue_reduce_ippon, "btn-secondary")
    enable_btn(blue_expand_ippon, "btn-secondary")
}

const whiteExpandWazaari = () => {
    timeops.white.wazaari = 'active'
    setOption("white:wazaari", 'active')
    document.getElementById("wazaari-white").innerText = "1"

    disable_btn(white_expand_wazaari, "btn-secondary")
    enable_btn(white_reduce_wazaari, "btn-secondary")
}
const whiteUnclearWazaari = () => {
    timeops.white.wazaari = 'pending'
    setOption("white:wazaari", 'pending')
    document.getElementById("wazaari-white").innerText = "(1)"

    enable_btn(white_expand_wazaari, "btn-secondary")
    enable_btn(white_reduce_wazaari, "btn-secondary")
}
const whiteReduceWazaari = () => {
    timeops.white.wazaari = false
    setOption("white:wazaari", '')
    document.getElementById("wazaari-white").innerText = "0"

    disable_btn(white_reduce_wazaari, "btn-secondary")
    enable_btn(white_expand_wazaari, "btn-secondary")
}

const blueExpandWazaari = () => {
    timeops.blue.wazaari = 'active'
    setOption("blue:wazaari", 'active')
    document.getElementById("wazaari-blue").innerText = "1"

    disable_btn(blue_expand_wazaari, "btn-secondary")
    enable_btn(blue_reduce_wazaari, "btn-secondary")
}
const blueUnclearWazaari = () => {
    timeops.blue.wazaari = 'pending'
    setOption("blue:wazaari", 'pending')
    document.getElementById("wazaari-blue").innerText = "(1)"

    enable_btn(blue_expand_wazaari, "btn-secondary")
    enable_btn(blue_reduce_wazaari, "btn-secondary")
}
const blueReduceWazaari = () => {
    timeops.blue.wazaari = false
    setOption("blue:wazaari", '')
    document.getElementById("wazaari-blue").innerText = "0"

    disable_btn(blue_reduce_wazaari, "btn-secondary")
    enable_btn(blue_expand_wazaari, "btn-secondary")
}

const whiteExpandShido = () => {
    if(timeops.white.shido == 3)
        return

    timeops.white.shido += 1
    setOption("white:shido", timeops.white.shido)
    document.getElementById("shido-white").innerText = timeops.white.shido

    white_reduce_shido.innerText = timeops.white.shido - 1
    if(timeops.white.shido == 3) {
        white_expand_shido.innerText = 3
        disable_btn(white_expand_shido, "btn-secondary")
    } else {
        white_expand_shido.innerText = timeops.white.shido + 1
    }
    
    enable_btn(white_reduce_shido, "btn-secondary")
}
const whiteReduceShido = () => {
    if(timeops.white.shido == 0)
        return

    timeops.white.shido -= 1
    setOption("white:shido", timeops.white.shido)
    document.getElementById("shido-white").innerText = timeops.white.shido

    white_expand_shido.innerText = timeops.white.shido + 1
    if(timeops.white.shido == 0) {
        white_reduce_shido.innerText = 0
        disable_btn(white_reduce_shido, "btn-secondary")
    } else {
        white_reduce_shido.innerText = timeops.white.shido - 1
    }
    
    enable_btn(white_expand_shido, "btn-secondary")
}

const blueExpandShido = () => {
    if(timeops.blue.shido == 3)
        return

    timeops.blue.shido += 1
    setOption("blue:shido", timeops.blue.shido)
    document.getElementById("shido-blue").innerText = timeops.blue.shido

    blue_reduce_shido.innerText = timeops.blue.shido - 1
    if(timeops.blue.shido == 3) {
        blue_expand_shido.innerText = 3
        disable_btn(blue_expand_shido, "btn-secondary")
    } else {
        blue_expand_shido.innerText = timeops.blue.shido + 1
    }
    
    enable_btn(blue_reduce_shido, "btn-secondary")
}
const blueReduceShido = () => {
    if(timeops.blue.shido == 0)
        return

    timeops.blue.shido -= 1
    setOption("blue:shido", timeops.blue.shido)
    document.getElementById("shido-blue").innerText = timeops.blue.shido

    blue_expand_shido.innerText = timeops.blue.shido + 1
    if(timeops.blue.shido == 0) {
        blue_reduce_shido.innerText = 0
        disable_btn(blue_reduce_shido, "btn-secondary")
    } else {
        blue_reduce_shido.innerText = timeops.blue.shido - 1
    }
    
    enable_btn(blue_expand_shido, "btn-secondary")
}

const whiteExpandHansokumake = () => {
    timeops.white.hansokumake = 'active'
    setOption("white:hansokumake", '1')
    document.getElementById("hansokumake-white").innerText = "H"

    disable_btn(white_expand_hansokumake, "btn-secondary")
    enable_btn(white_reduce_hansokumake, "btn-secondary")
}
const whiteReduceHansokumake = () => {
    timeops.white.hansokumake = false
    setOption("white:hansokumake", '0')
    document.getElementById("hansokumake-white").innerText = "-"

    disable_btn(white_reduce_hansokumake, "btn-secondary")
    enable_btn(white_expand_hansokumake, "btn-secondary")
}

const blueExpandHansokumake = () => {
    timeops.blue.hansokumake = 'active'
    setOption("blue:hansokumake", '1')
    document.getElementById("hansokumake-blue").innerText = "H"

    disable_btn(blue_expand_hansokumake, "btn-secondary")
    enable_btn(blue_reduce_hansokumake, "btn-secondary")
}
const blueReduceHansokumake = () => {
    timeops.blue.hansokumake = false
    setOption("blue:hansokumake", '0')
    document.getElementById("hansokumake-blue").innerText = "-"

    disable_btn(blue_reduce_hansokumake, "btn-secondary")
    enable_btn(blue_expand_hansokumake, "btn-secondary")
}

const setOption = (key, value) => {
    if (value != null)
        localStorage.setItem("tatami-scoreboard:" + key, value)
    else
        localStorage.removeItem("tatami-scoreboard:" + key)
}
const tick = () => {
    let now = Date.now()
    let differ = now - timeops.lastTick
    timeops.lastTick = now
    timeops.tickOnlyTime += differ
    if (timeops.ticking) timeops.globalTime -= differ
    if (timeops.ticking && timeops.globalTime <= 0) endTime()
    updateTime()
}

const disable_btn = (btn, active_color) => {
    btn.classList.remove(active_color)
    btn.classList.add("btn-outline-secondary")
    btn.setAttribute("disabled", true)
}
const enable_btn = (btn, active_color) => {
    btn.classList.add(active_color)
    btn.classList.remove("btn-outline-secondary")
    btn.removeAttribute("disabled")
}

main_view.addEventListener("click", mainView)
callup_view.addEventListener("click", callupView)
break_view.addEventListener("click", breakView)

start_time.addEventListener("click", startTime)
stop_time.addEventListener("click", stopTime)
flash_medical.addEventListener("click", flashMedical)

white_start_osaekomi.addEventListener("click", whiteStartOsaekomi)
white_stop_osaekomi.addEventListener("click", whiteStopOsaekomi)
blue_start_osaekomi.addEventListener("click", blueStartOsaekomi)
blue_stop_osaekomi.addEventListener("click", blueStopOsaekomi)

white_expand_ippon.addEventListener("click", whiteExpandIppon)
white_reduce_ippon.addEventListener("click", whiteReduceIppon)
blue_expand_ippon.addEventListener("click", blueExpandIppon)
blue_reduce_ippon.addEventListener("click", blueReduceIppon)

white_expand_wazaari.addEventListener("click", whiteExpandWazaari)
white_reduce_wazaari.addEventListener("click", whiteReduceWazaari)
blue_expand_wazaari.addEventListener("click", blueExpandWazaari)
blue_reduce_wazaari.addEventListener("click", blueReduceWazaari)

white_expand_shido.addEventListener("click", whiteExpandShido)
white_reduce_shido.addEventListener("click", whiteReduceShido)
blue_expand_shido.addEventListener("click", blueExpandShido)
blue_reduce_shido.addEventListener("click", blueReduceShido)

white_expand_hansokumake.addEventListener("click", whiteExpandHansokumake)
white_reduce_hansokumake.addEventListener("click", whiteReduceHansokumake)
blue_expand_hansokumake.addEventListener("click", blueExpandHansokumake)
blue_reduce_hansokumake.addEventListener("click", blueReduceHansokumake)

window.addEventListener("load", () => {
    setOption("reset", true)
    setTimeout(() => { setOption("view", "main") }, 50)
    initTime()
    timeops.lastTick = Date.now()
    setInterval(tick, 50)
})