/* Helpers */

const setOption = (key, value) => {
    if (value != null)
        localStorage.setItem("tatami-scoreboard:" + key, value)
    else
        localStorage.removeItem("tatami-scoreboard:" + key)
}

const disable_btn = (btn) => {
    btn.setAttribute("disabled", true)
}

const enable_btn = (btn) => {
    btn.removeAttribute("disabled")
}

/* Views */

const renderControls = () => {
    global_time.innerText = new Date(properIntegralConversion(sbState.time.displayTime / 1000) * 1000).toISOString().substr(15, 4)

    if (sbState.time.running) {
        disable_btn(start_time)
        enable_btn(stop_time)
        global_time.classList.add('running')
    } else {
        disable_btn(stop_time)
        enable_btn(start_time)
        global_time.classList.remove('running')
    }

    if (sbState.time.goldenScore) {
        global_time.classList.add("goldenscore")
    } else {
        global_time.classList.remove("goldenscore")
    }

    if (sbState.view.screen == 'main') {
        main_view.classList.add("active")
        callup_view.classList.remove("active")
        break_view.classList.remove("active")
    } else if (sbState.view.screen == 'callup') {
        main_view.classList.remove("active")
        callup_view.classList.add("active")
        break_view.classList.remove("active")
    } else if (sbState.view.screen == 'break') {
        main_view.classList.remove("active")
        callup_view.classList.remove("active")
        break_view.classList.add("active")
    } else if (sbState.view.screen == 'winner:white' || sbState.view.screen == 'winner:blue') {
        main_view.classList.remove("active")
        callup_view.classList.remove("active")
        break_view.classList.add("active")
    }

    if (sbState.view.medical) {
        flash_medical.classList.add("active")
    } else {
        flash_medical.classList.remove("active")
    }

    if (SBRULES.controls.includes('osaekomi')) {

        if (sbState.white.osaekomi.running) {
            disable_btn(white_start_osaekomi)
            enable_btn(white_stop_osaekomi)
            white_osaekomi.innerText = osaekomiTimeToSeconds(sbState.white.osaekomi.since)
        } else {
            disable_btn(white_stop_osaekomi)
            enable_btn(white_start_osaekomi)
            white_osaekomi.innerText = ""
        }

        if (sbState.blue.osaekomi.running) {
            disable_btn(blue_start_osaekomi)
            enable_btn(blue_stop_osaekomi)
            blue_osaekomi.innerText = osaekomiTimeToSeconds(sbState.blue.osaekomi.since)
        } else {
            disable_btn(blue_stop_osaekomi)
            enable_btn(blue_start_osaekomi)
            blue_osaekomi.innerText = ""
        }

        if (sbState.white.osaekomi.running) {
            enable_btn(toggle_osaekomi)
            toggle_osaekomi.innerText = 'Tauschen'
        } else if (sbState.blue.osaekomi.running) {
            enable_btn(toggle_osaekomi)
            toggle_osaekomi.innerText = 'Tauschen'
        } else {
            disable_btn(toggle_osaekomi)
            toggle_osaekomi.innerText = 'Tauschen'
        }

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
                let results_elems = document.querySelectorAll(
                    "[data-tatami-field='results." + side + "'][data-tatami-score='" + score_name + "']")

                let text = "" + sbState[side].scores[score_name].value
                if (sbState[side].scores[score_name].pending)
                    text = "(" + text + ")"

                up_elem.innerText = text

                results_elems.forEach((re) => {
                    re.innerText = text
                })

                if (score.pending || sbState[side].scores[score_name].value > 0)
                    enable_btn(down_elem)
                else
                    disable_btn(down_elem)

                if (!score.pending && score.max_count && sbState[side].scores[score_name].value >= score.max_count)
                    disable_btn(up_elem)
                else
                    enable_btn(up_elem)
            }
        }
    }
}

const renderBoard = () => {
    setOption("mat-number", mat_number)
    setOption("view", sbState.view.screen)

    setOption("time:main", properIntegralConversion(sbState.time.displayTime / 1000))
    setOption("time:running", sbState.time.running)

    if (sbState.time.goldenScore) {
        setOption("time:golden-score", "true")
    } else {
        setOption("time:golden-score", "false")
    }

    if (sbState.view.timeAlert) {
        setOption("time:flash-alert", true)
    } else {
        setOption("time:flash-alert", false)
    }

    if (sbState.view.medical) {
        setOption("time:flash-medical", true)
    } else {
        setOption("time:flash-medical", false)
    }

    if (sbState.white.osaekomi.running) {
        setOption("time:osaekomi:white", osaekomiTimeToSeconds(sbState.white.osaekomi.since))
    } else {
        setOption("time:osaekomi:white", -1)
    }

    if (sbState.blue.osaekomi.running) {
        setOption("time:osaekomi:blue", osaekomiTimeToSeconds(sbState.blue.osaekomi.since))
    } else {
        setOption("time:osaekomi:blue", -1)
    }

    for (const score_name in SBRULES.scores) {
        if (Object.prototype.hasOwnProperty.call(SBRULES.scores, score_name)) {
            const score = SBRULES.scores[score_name];

            setOption("white:" + score_name + ":pending", sbState.white.scores[score_name].pending ? 'yes' : 'no')
            setOption("blue:" + score_name + ":pending", sbState.blue.scores[score_name].pending ? 'yes' : 'no')

            if (score.is_equal_if_accumulated) {
                setOption("white:" + score_name + ":value", sbState.white.scores[score_name].value_with_accum)
                setOption("blue:" + score_name + ":value", sbState.blue.scores[score_name].value_with_accum)
            } else {
                setOption("white:" + score_name + ":value", sbState.white.scores[score_name].value)
                setOption("blue:" + score_name + ":value", sbState.blue.scores[score_name].value)
            }
        }
    }
}