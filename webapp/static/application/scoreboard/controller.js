const timeDefault = 120;
const start_time = document.querySelector("[data-control=\"time.main.start\"]")
const stop_time = document.querySelector("[data-control=\"time.main.stop\"]")

var timeops = {
    globalTime: 0,
    ticking: 0,
    lastTick: null
};

var globalTime, ticking;


const initTime = () => {
    timeops.globalTime = timeDefault * 1000;
    timeops.ticking = false;
    updateTime();
}
const updateTime = () => {
    setOption("time:main", Math.ceil(timeops.globalTime / 1000));
    setOption("time:running", timeops.ticking);
    document.getElementById("global-time").innerText = new Date(Math.ceil(timeops.globalTime / 1000) * 1000).toISOString().substr(15, 4)
}
const startTime = () => {
    timeops.ticking = true;
    
    start_time.classList.remove("btn-success")
    start_time.classList.add("btn-outline-secondary")
    start_time.setAttribute("disabled", true)

    stop_time.classList.add("btn-danger")
    stop_time.classList.remove("btn-outline-secondary")
    stop_time.removeAttribute("disabled")
}
const stopTime = () => {
    timeops.ticking = false;

    stop_time.classList.remove("btn-danger")
    stop_time.classList.add("btn-outline-secondary")
    stop_time.setAttribute("disabled", true)

    start_time.classList.add("btn-success")
    start_time.classList.remove("btn-outline-secondary")
    start_time.removeAttribute("disabled")
}

start_time.addEventListener("click", startTime);
function endTime() {
    stopTime();
    timeops.globalTime = 0;
    setOption("time:flash-alert", true);
    setTimeout(() => {
        setOption("time:flash-alert", false);
    }, 3000);
}
function setOption(key, value) {
    if (value != null)
        localStorage.setItem("tatami-scoreboard:" + key, value);
    else
        localStorage.removeItem("tatami-scoreboard:" + key);
}
function tick() {
    let now = Date.now();
    let differ = now - timeops.lastTick;
    timeops.lastTick = now;
    if (timeops.ticking) timeops.globalTime -= differ;
    if (timeops.ticking && timeops.globalTime <= 0) endTime();
    updateTime();
}

window.addEventListener("load", () => {
    initTime();
    timeops.lastTick = Date.now();
    setInterval(tick, 50);
});