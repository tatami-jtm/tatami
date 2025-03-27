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
const correct_time = document.querySelector("[data-control=\"time.main.correct\"]")
const flash_medical = document.querySelector("[data-control=\"flash.medical\"]")

const toggle_osaekomi = document.querySelector("[data-control=\"osaekomi.toggle\"]")

const white_start_osaekomi = document.querySelector("[data-control=\"osaekomi.white.start\"]")
const white_stop_osaekomi = document.querySelector("[data-control=\"osaekomi.white.stop\"]")
const blue_start_osaekomi = document.querySelector("[data-control=\"osaekomi.blue.start\"]")
const blue_stop_osaekomi = document.querySelector("[data-control=\"osaekomi.blue.stop\"]")

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
    start_time.blur()
})
stop_time.addEventListener("click", () => {
    sbState.time.running = false
    stop_time.blur()
})

correct_time.addEventListener("click", () => {
    correct_time.blur()
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
        sbState.time.goldenScore = false
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
    main_view.blur()
})
callup_view.addEventListener("click", () => {
    sbState.view.screen = 'callup'
    callup_view.blur()
})
break_view.addEventListener("click", () => {
    sbState.view.screen = 'break'
    break_view.blur()
})

/* Control: Medical Alert */
flash_medical.addEventListener("click", () => {
    sbState.view.medical = !sbState.view.medical
    flash_medical.blur()
})

if (SBRULES.controls.includes('osaekomi')) {

    /* Control: Osaekomi */
    white_start_osaekomi.addEventListener("click", () => {
        sbState.white.osaekomi.running = true
        sbState.white.osaekomi.since = sbState.time.globalTick
        sbState.white.osaekomi.scores_given = []
        sbState.blue.osaekomi.running = false
        white_start_osaekomi.blur()
    })
    white_stop_osaekomi.addEventListener("click", () => {
        sbState.white.osaekomi.running = false
        white_stop_osaekomi.blur()
    })

    blue_start_osaekomi.addEventListener("click", () => {
        sbState.blue.osaekomi.running = true
        sbState.blue.osaekomi.since = sbState.time.globalTick
        sbState.blue.osaekomi.scores_given = []
        sbState.white.osaekomi.running = false
        blue_start_osaekomi.blur()
    })
    blue_stop_osaekomi.addEventListener("click", () => {
        sbState.blue.osaekomi.running = false
        blue_stop_osaekomi.blur()
    })

    toggle_osaekomi.addEventListener("click", () => {
        if(sbState.blue.osaekomi.running) {
            sbState.blue.osaekomi.running = false
            sbState.white.osaekomi.running = true
            sbState.white.osaekomi.since = sbState.blue.osaekomi.since
            sbState.white.osaekomi.scores_given = []

            sbState.blue.osaekomi.scores_given.forEach((score) => {
                if (sbState.blue.scores[score].value > 0) {
                    sbState.blue.scores[score].value -= 1
                    sbState.blue.scores[score].pending = false
                }
            })
        } else if(sbState.white.osaekomi.running) {
            sbState.white.osaekomi.running = false
            sbState.blue.osaekomi.running = true
            sbState.blue.osaekomi.since = sbState.white.osaekomi.since
            sbState.blue.osaekomi.scores_given = []

            sbState.white.osaekomi.scores_given.forEach((score) => {
                if (sbState.white.scores[score].value > 0) {
                    sbState.white.scores[score].value -= 1
                    sbState.white.scores[score].pending = false
                }
            })
        }

        toggle_osaekomi.blur()
    })

}

let sides = ['white', 'blue']
for (const side of sides) {
    for (const score_name in SBRULES.scores) {
        if (Object.prototype.hasOwnProperty.call(SBRULES.scores, score_name)) {
            const score = SBRULES.scores[score_name];

            let up_elem = document.querySelector(
                "[data-control='" + side + ".expand'][data-score='" + score_name + "']")
            let down_elem = document.querySelector(
                "[data-control='" + side + ".reduce'][data-score='" + score_name + "']")

            up_elem.addEventListener('click', () => {
                if (sbState[side].scores[score_name].pending)
                    sbState[side].scores[score_name].pending = false
                else
                    if (score.max_count && sbState[side].scores[score_name].value >= score.max_count)
                        return
                    else
                        sbState[side].scores[score_name].value += 1
            });

            down_elem.addEventListener('click', () => {
                sbState[side].scores[score_name].pending = false

                if (sbState[side].scores[score_name].value == 0)
                    return

                sbState[side].scores[score_name].value -= 1
            });
        }
    }
}