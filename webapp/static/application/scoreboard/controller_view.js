/* Helpers */

const setOption = (key, value) => {
    if (value != null)
        localStorage.setItem("tatami-scoreboard:" + key, value)
    else
        localStorage.removeItem("tatami-scoreboard:" + key)
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

/* Views */

const renderControls = () => {
    global_time.innerText = new Date(properIntegralConversion(sbState.time.displayTime / 1000) * 1000).toISOString().substr(15, 4)

    if (sbState.time.running) {
        disable_btn(start_time, "btn-success")
        enable_btn(stop_time, "btn-danger")
        global_time.parentNode.classList.add('running')
    } else {
        disable_btn(stop_time, "btn-danger")
        enable_btn(start_time, "btn-success")
        global_time.parentNode.classList.remove('running')
    }

    if (sbState.time.goldenScore) {
        global_time.parentNode.classList.add("goldenscore")
    } else {
        global_time.parentNode.classList.remove("goldenscore")
    }

    if (sbState.view.screen == 'main') {
        main_view.classList.add("active")
        callup_view.classList.remove("active")
        break_view.classList.remove("active")
        current_screen.innerText = "- Kampf -"
    } else if (sbState.view.screen == 'callup') {
        main_view.classList.remove("active")
        callup_view.classList.add("active")
        break_view.classList.remove("active")
        current_screen.innerText = "- Aufruf -"
    } else if (sbState.view.screen == 'break') {
        main_view.classList.remove("active")
        callup_view.classList.remove("active")
        break_view.classList.add("active")
        current_screen.innerText = "- Pause -"
    } else if (sbState.view.screen == 'winner:white' || sbState.view.screen == 'winner:blue') {
        main_view.classList.remove("active")
        callup_view.classList.remove("active")
        break_view.classList.add("active")
        current_screen.innerText = "- Gewinner*in wird angezeigt -"
    }

    if (sbState.view.medical) {
        flash_medical.classList.add("active")
    } else {
        flash_medical.classList.remove("active")
    }

    if (sbState.white.osaekomi.running) {
        disable_btn(white_start_osaekomi, "btn-secondary")
        enable_btn(white_stop_osaekomi, "btn-secondary")
        white_osaekomi.innerText = osaekomiTimeToSeconds(sbState.white.osaekomi.since)
    } else {
        disable_btn(white_stop_osaekomi, "btn-secondary")
        enable_btn(white_start_osaekomi, "btn-secondary")
        white_osaekomi.innerText = ""
    }

    if (sbState.blue.osaekomi.running) {
        disable_btn(blue_start_osaekomi, "btn-secondary")
        enable_btn(blue_stop_osaekomi, "btn-secondary")
        blue_osaekomi.innerText = osaekomiTimeToSeconds(sbState.blue.osaekomi.since)
    } else {
        disable_btn(blue_stop_osaekomi, "btn-secondary")
        enable_btn(blue_start_osaekomi, "btn-secondary")
        blue_osaekomi.innerText = ""
    }

    if (sbState.white.osaekomi.running) {
        enable_btn(toggle_osaekomi, 'btn-secondary')
        toggle_osaekomi.innerText = 'Tauschen »'
    } else if (sbState.blue.osaekomi.running) {
        enable_btn(toggle_osaekomi, 'btn-secondary')
        toggle_osaekomi.innerText = '« Tauschen'
    } else {
        disable_btn(toggle_osaekomi, 'btn-secondary')
        toggle_osaekomi.innerText = '« Tauschen »'
    }

    if (sbState.white.ippon) {
        ippon_white.innerText = "1"
        disable_btn(white_expand_ippon, "btn-secondary")
        enable_btn(white_reduce_ippon, "btn-secondary")
    } else {
        ippon_white.innerText = "0"
        disable_btn(white_reduce_ippon, "btn-secondary")
        enable_btn(white_expand_ippon, "btn-secondary")
    }

    if (sbState.blue.ippon) {
        ippon_blue.innerText = "1"
        disable_btn(blue_expand_ippon, "btn-secondary")
        enable_btn(blue_reduce_ippon, "btn-secondary")
    } else {
        ippon_blue.innerText = "0"
        disable_btn(blue_reduce_ippon, "btn-secondary")
        enable_btn(blue_expand_ippon, "btn-secondary")
    }

    if (sbState.white.wazaari_awasete_ippon) {
        wazaari_white.innerText = "2"
        disable_btn(white_expand_wazaari, "btn-secondary")
        enable_btn(white_reduce_wazaari, "btn-secondary")
    } else if (sbState.white.wazaari) {
        wazaari_white.innerText = "1"
        enable_btn(white_expand_wazaari, "btn-secondary")
        enable_btn(white_reduce_wazaari, "btn-secondary")
    } else if (sbState.white.wazaari_pending) {
        wazaari_white.innerText = "(1)"
        enable_btn(white_expand_wazaari, "btn-secondary")
        enable_btn(white_reduce_wazaari, "btn-secondary")
    } else {
        wazaari_white.innerText = "0"
        disable_btn(white_reduce_wazaari, "btn-secondary")
        enable_btn(white_expand_wazaari, "btn-secondary")
    }

    if (sbState.blue.wazaari_awasete_ippon) {
        wazaari_blue.innerText = "2"
        disable_btn(blue_expand_wazaari, "btn-secondary")
        enable_btn(blue_reduce_wazaari, "btn-secondary")
    } else if (sbState.blue.wazaari) {
        wazaari_blue.innerText = "1"
        enable_btn(blue_expand_wazaari, "btn-secondary")
        enable_btn(blue_reduce_wazaari, "btn-secondary")
    } else if (sbState.blue.wazaari_pending) {
        wazaari_blue.innerText = "(1)"
        enable_btn(blue_expand_wazaari, "btn-secondary")
        enable_btn(blue_reduce_wazaari, "btn-secondary")
    } else {
        wazaari_blue.innerText = "0"
        disable_btn(blue_reduce_wazaari, "btn-secondary")
        enable_btn(blue_expand_wazaari, "btn-secondary")
    }

    shido_white.innerText = sbState.white.shido
    shido_blue.innerText = sbState.blue.shido

    if (sbState.white.shido == 3) {
        white_expand_shido.innerText = 3
        disable_btn(white_expand_shido, "btn-secondary")
        enable_btn(white_reduce_shido, "btn-secondary")
    } else if (sbState.white.shido == 0) {
        white_expand_shido.innerText = 0
        disable_btn(white_reduce_shido, "btn-secondary")
        enable_btn(white_expand_shido, "btn-secondary")
    } else {
        white_expand_shido.innerText = sbState.white.shido
        enable_btn(white_expand_shido, "btn-secondary")
        enable_btn(white_reduce_shido, "btn-secondary")
    }

    if (sbState.blue.shido == 3) {
        blue_expand_shido.innerText = 3
        disable_btn(blue_expand_shido, "btn-secondary")
        enable_btn(blue_reduce_shido, "btn-secondary")
    } else if (sbState.blue.shido == 0) {
        blue_expand_shido.innerText = 0
        disable_btn(blue_reduce_shido, "btn-secondary")
        enable_btn(blue_expand_shido, "btn-secondary")
    } else {
        blue_expand_shido.innerText = sbState.blue.shido
        enable_btn(blue_expand_shido, "btn-secondary")
        enable_btn(blue_reduce_shido, "btn-secondary")
    }

    if (sbState.white.hansokumake) {
        hansokumake_white.innerText = "1"
        disable_btn(white_expand_hansokumake, "btn-secondary")
        enable_btn(white_reduce_hansokumake, "btn-secondary")
    } else {
        hansokumake_white.innerText = "0"
        disable_btn(white_reduce_hansokumake, "btn-secondary")
        enable_btn(white_expand_hansokumake, "btn-secondary")
    }

    if (sbState.blue.hansokumake) {
        hansokumake_blue.innerText = "1"
        disable_btn(blue_expand_hansokumake, "btn-secondary")
        enable_btn(blue_reduce_hansokumake, "btn-secondary")
    } else {
        hansokumake_blue.innerText = "0"
        disable_btn(blue_reduce_hansokumake, "btn-secondary")
        enable_btn(blue_expand_hansokumake, "btn-secondary")
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

    if (sbState.white.ippon) {
        setOption("white:ippon", 1)
    } else {
        setOption("white:ippon", 0)
    }

    if (sbState.blue.ippon) {
        setOption("blue:ippon", 1)
    } else {
        setOption("blue:ippon", 0)
    }

    if (sbState.white.wazaari_awasete_ippon) {
        setOption("white:wazaari", '')
        setOption("white:ippon", 1)
    } else if (sbState.white.wazaari) {
        setOption("white:wazaari", 'active')
    } else if (sbState.white.wazaari_pending) {
        setOption("white:wazaari", 'pending')
    } else {
        setOption("white:wazaari", '')
    }

    if (sbState.blue.wazaari_awasete_ippon) {
        setOption("blue:ippon", 1)
        setOption("blue:wazaari", '')
    } else if (sbState.blue.wazaari) {
        setOption("blue:wazaari", 'active')
    } else if (sbState.blue.wazaari_pending) {
        setOption("blue:wazaari", 'pending')
    } else {
        setOption("blue:wazaari", '')
    }

    setOption("white:shido", sbState.white.shido)
    setOption("blue:shido", sbState.blue.shido)

    if (sbState.white.hansokumake) {
        setOption("white:hansokumake", 1)
    } else {
        setOption("white:hansokumake", 0)
    }

    if (sbState.blue.hansokumake) {
        setOption("blue:hansokumake", 1)
    } else {
        setOption("blue:hansokumake", 0)
    }
}