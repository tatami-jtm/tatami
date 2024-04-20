var local_config = {
    fightDuration: 240,
    hasGoldenScore: true,
    maxGoldenScore: null,
    defaultScreen: 'callup'
}

const enter_results = document.querySelector("[data-control=\"enter-results\"]")
const transactional_end_fight = enter_results

const scheduledArea = document.querySelector('[data-scheduled-area]')
const resultsModal = new bootstrap.Modal('#results-modal')
const callupModal = new bootstrap.Modal('#callup-modal')

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

    scheduledArea.outerHTML = reply
    updateLocalConfig()
    updateFromSource()
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

        document.querySelector('.callup-next-hasnot').classList.add('d-none')
        document.querySelector('.callup-next-has').classList.remove('d-none')
    } else {
        document.querySelector('.callup-next-hasnot').classList.remove('d-none')
        document.querySelector('.callup-next-has').classList.add('d-none')
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
    }


    if (document.querySelector("[data-tatami-source=\"waiting_match.any\"]").value == '1') {
        setOption("prepare:class", document.querySelector("[data-tatami-source=\"waiting_match.group\"]").value)
        setOption("prepare:progress", document.querySelector("[data-tatami-source=\"waiting_match.progress\"]").value)
        setOption("prepare:white:name", document.querySelector("[data-tatami-source=\"waiting_match.white.name\"]").value)
        setOption("prepare:white:club", document.querySelector("[data-tatami-source=\"waiting_match.white.association\"]").value)
        setOption("prepare:blue:name", document.querySelector("[data-tatami-source=\"waiting_match.blue.name\"]").value)
        setOption("prepare:blue:club", document.querySelector("[data-tatami-source=\"waiting_match.blue.association\"]").value)
    }

    updateField("results.white.ippon", (sbState.white.ippon) ? 1 : 0)
    updateField("results.white.wazaari", (sbState.white.wazaari_awasete_ippon) ? 2 : (sbState.white.wazaari) ? 1 : 0)
    updateField("results.white.shido", sbState.white.shido)
    updateField("results.white.hansokumake", (sbState.white.hansokumake) ? 1 : 0)

    updateField("results.blue.ippon", (sbState.blue.ippon) ? 1 : 0)
    updateField("results.blue.wazaari", (sbState.blue.wazaari_awasete_ippon) ? 2 : (sbState.blue.wazaari) ? 1 : 0)
    updateField("results.blue.shido", sbState.blue.shido)
    updateField("results.blue.hansokumake", (sbState.blue.hansokumake) ? 1 : 0)
    updateField("results.full_time", printFullTime(sbState))
}

window.addEventListener("load", () => {
    startNewMatch()
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

    if (document.querySelector("[data-tatami-source=\"current_match.any\"]").value == '1') {
        callupModal.show()
        document.querySelector("[data-tatami-end-callup]").focus()
    } else {
        sbState.view.screen = 'break'
    }
}

document.querySelector("[data-tatami-end-callup]").addEventListener("click", () => {
    sbState.view.screen = 'main'
    callupModal.hide()
})

document.querySelector("[data-tatami-enter-results]").addEventListener("click", async () => {
    resultsModal.hide()

    let formData = new FormData()
    
    formData.append('is_api', 'yup')
    formData.append('winner', document.getElementById('match-winner').value)
    formData.append('score', document.getElementById('match-score').value)

    document.getElementById('match-winner').options.selectedIndex = 0;
    document.getElementById('match-score').options.selectedIndex = 0;

    if (document.getElementById('match-loser-disqualified').checked)
        formData.append('loser_disqualified', 1)

    if (document.getElementById('match-loser-removed').checked)
        formData.append('loser_removed', 1)

    formData.append('sb-white-ippon', (sbState.white.ippon) ? 1 : 0)
    formData.append('sb-white-wazaari', (sbState.white.wazaari_awasete_ippon) ? 2 : (sbState.white.wazaari) ? 1 : 0)
    formData.append('sb-white-shido', sbState.white.shido)
    formData.append('sb-white-hansokumake', (sbState.white.hansokumake) ? 1 : 0)

    formData.append('sb-blue-ippon', (sbState.blue.ippon) ? 1 : 0)
    formData.append('sb-blue-wazaari', (sbState.blue.wazaari_awasete_ippon) ? 2 : (sbState.blue.wazaari) ? 1 : 0)
    formData.append('sb-blue-shido', sbState.blue.shido)
    formData.append('sb-blue-hansokumake', (sbState.blue.hansokumake) ? 1 : 0)

    let displayTime = getFullTime(sbState)
    let mins = Math.floor(displayTime / 60)
    let secs = displayTime % 60

    formData.append('ft-minutes', mins)
    formData.append('ft-seconds', secs)

    let response = await fetch(document.querySelector("[data-tatami-source=\"current_match.results_link\"]").value, {
        method: 'POST',
        body: formData
    })
    let reply = await response.json()

    if (reply.status == 'error') {
        alert(`Fehler: ${reply.message}`)
    } else if (reply.status == 'success') {
        await update_schedule()
        startNewMatch()
    }
})