const scheduledArea = document.querySelector('[data-scheduled-area]')

scheduledArea.addEventListener('click', async (e) => {
    let event = document.body.getAttribute("data-tatami-event")

    if (e.target.hasAttribute('data-schedule-match')) {
        matchToSchedule = e.target.getAttribute('data-schedule-match')

        let response = await fetch(`/go/${event}/mod_list/api/schedule/${matchToSchedule}`)
        let reply = await response.json()

        if(reply.status == 'error') {
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
    let response = await fetch(`/go/${event}/mod_list/api/reload`)
    let reply = await response.text()

    scheduledArea.outerHTML = reply
}