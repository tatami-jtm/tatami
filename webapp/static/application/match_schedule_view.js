var local_config = {
    fightDuration: 0,
    hasGoldenScore: true,
    maxGoldenScore: null,
    defaultScreen: 'break'
}

var repeated_call = {
    time: 60,
    running: false,
    running_since: null
}

const enter_results = document.querySelector("[data-control=\"enter-results\"]")
const transactional_end_fight = enter_results
const callup_again = document.querySelector("[data-control=\"callup-again\"]")
const callup_now = document.querySelector("[data-control=\"callup\"]")

const repeated_call_btn = document.querySelector("[data-tatami-repeated-call]")

const scheduledArea = document.querySelector('[data-scheduled-area]')
const resultsModal = document.querySelector('#results-modal')
const callupModal = document.querySelector('#callup-modal')
const winnerShownModal = document.querySelector('#winner-shown-modal')
const offlineModal = document.querySelector('#offline-modal')

scheduledArea.addEventListener('click', async (e) => {
    let event = document.body.getAttribute("data-tatami-event")

    if (e.target.hasAttribute('data-schedule-match')) {
        matchToSchedule = e.target.getAttribute('data-schedule-match')

        let response = await fetch(`/go/${event}/mod_list/api/schedule/${matchToSchedule}`)
        let reply = await response.json()

        if (reply.status == 'error') {
            alert(`Fehler: ${reply.message}`)
        } else if (reply.status == 'success') {
            if ((typeof forceLocalUpdate == 'undefined') || !forceLocalUpdate) {
                location.reload()
            } else {
                await update_schedule()
            }
        }
    }
})

let update_schedule = async (e) => {
    let event = document.body.getAttribute("data-tatami-event")
    let response = await fetch(`/go/${event}/mod_scoreboard/managed/api/reload`)
    let reply = await response.text()

    scheduledArea.innerHTML = reply
    updateLocalConfig()
    updateFromSource()
    enable_TJ(scheduledArea)
}

const updateField = (field, value) => {
    document.querySelectorAll(`[data-tatami-field="${field}"]`).forEach((f) => {
        f.innerText = value
    })
}

const updateFromSource = () => {
    if (document.querySelector("[data-tatami-source=\"current_match.any\"]").value == '1') {
        updateField("results.white.entry", "Weiß (" + document.querySelector("[data-tatami-source=\"current_match.white.name\"]").value + ")")
        updateField("results.blue.entry", "Blau (" + document.querySelector("[data-tatami-source=\"current_match.blue.name\"]").value + ")")

        updateField("current.white.name", document.querySelector("[data-tatami-source=\"current_match.white.name\"]").value)
        updateField("current.white.club", document.querySelector("[data-tatami-source=\"current_match.white.association\"]").value)
        updateField("current.blue.name", document.querySelector("[data-tatami-source=\"current_match.blue.name\"]").value)
        updateField("current.blue.club", document.querySelector("[data-tatami-source=\"current_match.blue.association\"]").value)
        updateField("current.group", document.querySelector("[data-tatami-source=\"current_match.group\"]").value)
        updateField("current.progress", document.querySelector("[data-tatami-source=\"current_match.progress\"]").value)
    }
    
    if (document.querySelector("[data-tatami-source=\"waiting_match.any\"]").value == '1') {
        updateField("waiting.white.name", document.querySelector("[data-tatami-source=\"waiting_match.white.name\"]").value)
        updateField("waiting.white.club", document.querySelector("[data-tatami-source=\"waiting_match.white.association\"]").value)
        updateField("waiting.blue.name", document.querySelector("[data-tatami-source=\"waiting_match.blue.name\"]").value)
        updateField("waiting.blue.club", document.querySelector("[data-tatami-source=\"waiting_match.blue.association\"]").value)
        updateField("waiting.group", document.querySelector("[data-tatami-source=\"waiting_match.group\"]").value)
        updateField("waiting.progress", document.querySelector("[data-tatami-source=\"waiting_match.progress\"]").value)

        document.querySelector('.callup-next-hasnot').classList.add('hidden')
        document.querySelector('.callup-next-has').classList.remove('hidden')
    } else {
        document.querySelector('.callup-next-hasnot').classList.remove('hidden')
        document.querySelector('.callup-next-has').classList.add('hidden')
    }

}

const managedTick = () => {
    if (document.querySelector("[data-tatami-source=\"current_match.any\"]").value == '1') {
        setOption("class", document.querySelector("[data-tatami-source=\"current_match.group\"]").value)
        setOption("progress", document.querySelector("[data-tatami-source=\"current_match.progress\"]").value)
        setOption("white:name", document.querySelector("[data-tatami-source=\"current_match.white.name\"]").value)
        setOption("white:club", document.querySelector("[data-tatami-source=\"current_match.white.association\"]").value)
        setOption("blue:name", document.querySelector("[data-tatami-source=\"current_match.blue.name\"]").value)
        setOption("blue:club", document.querySelector("[data-tatami-source=\"current_match.blue.association\"]").value)
    } else {
        setOption("class", '')
        setOption("progress", '')
        setOption("white:name", '')
        setOption("white:club", '')
        setOption("blue:name", '')
        setOption("blue:club", '')
    }


    if (document.querySelector("[data-tatami-source=\"waiting_match.any\"]").value == '1') {
        setOption("prepare:class", document.querySelector("[data-tatami-source=\"waiting_match.group\"]").value)
        setOption("prepare:progress", document.querySelector("[data-tatami-source=\"waiting_match.progress\"]").value)
        setOption("prepare:white:name", document.querySelector("[data-tatami-source=\"waiting_match.white.name\"]").value)
        setOption("prepare:white:club", document.querySelector("[data-tatami-source=\"waiting_match.white.association\"]").value)
        setOption("prepare:blue:name", document.querySelector("[data-tatami-source=\"waiting_match.blue.name\"]").value)
        setOption("prepare:blue:club", document.querySelector("[data-tatami-source=\"waiting_match.blue.association\"]").value)
    } else {
        setOption("prepare:class", '')
        setOption("prepare:progress", '')
        setOption("prepare:white:name", '')
        setOption("prepare:white:club", '')
        setOption("prepare:blue:name", '')
        setOption("prepare:blue:club", '')
    }

    updateField("results.full_time", printFullTime(sbState))
}

window.addEventListener("load", () => {
    setInterval(managedTick, 50)
})

const getFullTime = (sbState) => {
    let displayTime = Math.ceil(sbState.time.displayTime/1000)

    if (sbState.time.goldenScore) {
        displayTime += sbState.config.fightDuration
    } else {
        displayTime = sbState.config.fightDuration - displayTime
    }

    return displayTime
}

const printFullTime = (sbState) => {
    let displayTime = getFullTime(sbState)
    let mins = Math.floor(displayTime / 60)
    let secs = displayTime % 60

    return `${mins}min ${secs}s`
}

const updateLocalConfig = () => {
    if (document.querySelector("[data-tatami-source=\"current_match.any\"]").value == '1') {
        let fighting_time = parseInt(document.querySelector("[data-tatami-source=\"current_match.fighting_time\"]").value)
        let golden_score_time = parseInt(document.querySelector("[data-tatami-source=\"current_match.golden_score_time\"]").value)

        local_config.fightDuration = fighting_time
        local_config.hasGoldenScore = golden_score_time != 0
        local_config.maxGoldenScore = (golden_score_time <= 0) ? null : golden_score_time
    }
}

const startNewMatch = () => {
    updateLocalConfig()
    updateFromSource()
    resetState(local_config)
    sbState.view.screen = 'callup'

    repeated_call.running = true
    repeated_call.running_since = Date.now()

    if (document.querySelector("[data-tatami-source=\"current_match.any\"]").value == '1') {
        callupModal.classList.add('shown')
        document.querySelector("[data-tatami-end-callup]").focus()
    } else {
        sbState.view.screen = 'break'
    }
}

document.querySelector("[data-tatami-end-callup]").addEventListener("click", () => {
    sbState.view.screen = 'main'
    repeated_call.running = false
    callupModal.classList.remove('shown')
})

document.querySelectorAll("[data-tatami-enter-results]").forEach((btn) => {
    btn.addEventListener("click", async () => {
        offlineModal.classList.remove('shown')
        if (document.getElementById('match-winner').value == 'white') {
            sbState.view.screen = 'winner:white'
            setOption('winner:name', document.querySelector("[data-tatami-source=\"current_match.white.name\"]").value)
            setOption('winner:club', document.querySelector("[data-tatami-source=\"current_match.white.association\"]").value)
            updateField("winner.name", document.querySelector("[data-tatami-source=\"current_match.white.name\"]").value)
            updateField("winner.club", document.querySelector("[data-tatami-source=\"current_match.white.association\"]").value)
        } else if (document.getElementById('match-winner').value == 'blue') {
            sbState.view.screen = 'winner:blue'
            setOption('winner:name', document.querySelector("[data-tatami-source=\"current_match.blue.name\"]").value)
            setOption('winner:club', document.querySelector("[data-tatami-source=\"current_match.blue.association\"]").value)
            updateField("winner.name", document.querySelector("[data-tatami-source=\"current_match.blue.name\"]").value)
            updateField("winner.club", document.querySelector("[data-tatami-source=\"current_match.blue.association\"]").value)
        } else {
            // No winner selected; aborting.
            return;
        }

        let formData = new FormData()
        
        formData.append('is_api', 'yup')
        formData.append('winner', document.getElementById('match-winner').value)
        formData.append('score', document.getElementById('match-score').value)

        if (document.getElementById('match-loser-disqualified').checked)
            formData.append('loser_disqualified', 1)

        if (document.getElementById('match-loser-removed').checked)
            formData.append('loser_removed', 1)

        let sides = ['white', 'blue']
        for (const side of sides) {
            for (const score_name in SBRULES.scores) {
                if (Object.prototype.hasOwnProperty.call(SBRULES.scores, score_name)) {   
                    formData.append('sb-' + side + '-' + score_name, sbState[side].scores[score_name].value)
                }
            }
        }

        let displayTime = getFullTime(sbState)
        let mins = Math.floor(displayTime / 60)
        let secs = displayTime % 60

        formData.append('ft-minutes', mins)
        formData.append('ft-seconds', secs)

        let response;
        try {
            response = await fetch(
                document.querySelector("[data-tatami-source=\"current_match.results_link\"]").value,
                {
                    method: 'POST',
                    body: formData
                }
            )
        } catch (error) {
            response = {
                ok: false,
                status: 'TATAMI ist offline:',
                statusText: error || ''
            }
        }

        console.log(response)

        if (response.ok) {
            let reply = await response.json()
            if (reply.status == 'error') {
                document.getElementById('offline-error-message').innerText = reply.message || 'unbekannt'
                resultsModal.classList.remove('shown')
                offlineModal.classList.add('shown')
            } else if (reply.status == 'success') {
                resultsModal.classList.remove('shown')
                winnerShownModal.classList.add('shown')

                await update_schedule()

                document.getElementById('match-winner').options.selectedIndex = 0;
                document.getElementById('match-score').options.selectedIndex = 0;
                document.getElementById('match-loser-disqualified').checked = false;
                document.getElementById('match-loser-removed').checked = false;

                callup_again.innerText = 'Kampf aufrufen'
                callup_again.classList.add('btn-secondary')
                callup_again.classList.remove('btn-danger-subtle')

                enter_results.classList.add('disabled')
            }
        } else {
            document.getElementById('offline-error-message').innerText = response.status + " " + response.statusText
            resultsModal.classList.remove('shown')
            offlineModal.classList.add('shown')
        }
    })
})

enter_results.addEventListener('click', () => {
    winner = determineWinner(true)

    if (winner == false) {
        document.getElementById('match-score').value = null
        document.getElementById('match-winner').value = null
    } else {
        let winning_points = winner[1]
        winner = winner[0]
    
        document.getElementById('match-score').value = winning_points
        document.getElementById('match-winner').value = winner
    }

    resultsModal.classList.add('shown')
})

let do_callup = () => {
    winnerShownModal.classList.remove('shown')
    startNewMatch()

    callup_again.innerText = 'Erneut aufrufen'
    callup_again.classList.remove('btn-secondary')
    callup_again.classList.add('btn-danger-subtle')

    enter_results.classList.remove('disabled');
    console.log(enter_results)
}

callup_now.addEventListener('click', do_callup);
callup_again.addEventListener('click', do_callup)

let repeated_call_view = () => {
    if (repeated_call.running) {
        time_remaining = Math.ceil(repeated_call.time - (Date.now() - repeated_call.running_since) / 1000)

        if (time_remaining > 0) {
            repeated_call_btn.innerText = time_remaining
            repeated_call_btn.classList.remove('pending')
            repeated_call_btn.setAttribute('disabled', true)
        } else {
            repeated_call_btn.classList.add('pending')
            repeated_call_btn.removeAttribute('disabled')
        }
    }
}

let repeated_call_reset = () => {
    if (!repeated_call_btn.hasAttribute('disabled'))
        repeated_call.running_since = Date.now()
}

setInterval(repeated_call_view, 50)
repeated_call_btn.addEventListener('click', repeated_call_reset)

document.querySelectorAll('[data-show-list]').forEach((sl) => {
    sl.addEventListener('click', (e) => {
        e.preventDefault()
        url = e.target.href;
        window.open(url, '_blank', "popup,width=600, height=700")
    })
})