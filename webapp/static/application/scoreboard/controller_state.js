/* Model */

const makeState = (config) => {
    return {
        view: {
            screen: config.defaultScreen || 'break',
            medicalAlert: false,
            timeAlert: false
        },
        config: config,
        time: {
            globalTick: 0,
            lastTick: Date.now(),

            running: false,
            displayTimeDirection: -1,
            displayTime: config.fightDuration * 1000,
            goldenScore: false
        },
        white: {
            osaekomi: {
                running: false,
                since: null,
                wazaari_given: false
            },
            ippon: false,
            wazaari: false,
            wazaari_pending: false,
            wazaari_awasete_ippon: false,
            shido: 0,
            hansokumake: false
        },
        blue: {
            osaekomi: {
                running: false,
                since: null,
                wazaari_given: false
            },
            ippon: false,
            wazaari: false,
            wazaari_pending: false,
            wazaari_awasete_ippon: false,
            shido: 0,
            hansokumake: false
        }
    }
}

const tick = () => {
    let now = Date.now()
    let differ = now - sbState.time.lastTick
    sbState.time.lastTick = now

    if (sbState.time.running) {
        sbState.time.globalTick += differ

        osaekomiCheck()

        effectiveNewTime = sbState.time.displayTime + (differ * sbState.time.displayTimeDirection)

        if (effectiveNewTime < 0)
            endOfTime()
        else if (sbState.time.goldenScore && sbState.config.maxGoldenScore && sbState.time.displayTime > sbState.config.maxGoldenScore * 1000)
            endOfTime()
        else
            sbState.time.displayTime = effectiveNewTime
    }
}

const endOfTime = (becauseOfOseakomi) => {
    if (!sbState.time.goldenScore && !becauseOfOseakomi) {
        sbState.time.displayTime = 0
    }

    if (sbState.white.osaekomi.running || sbState.blue.osaekomi.running)
        return

    sbState.view.timeAlert = true
    sbState.time.running = false

    setTimeout(() => {
        sbState.view.timeAlert = false
    }, 3000)

    let winner = determineWinner(true)
    if (winner)
        return

    if (!sbState.time.goldenScore && sbState.config.hasGoldenScore) {
        sbState.time.goldenScore = true
        sbState.time.displayTimeDirection = 1
    }
}

const osaekomiCheck = () => {
    if (sbState.white.osaekomi.running) {
        white_osaekomi_time = osaekomiTimeToSeconds(sbState.white.osaekomi.since)

        if (white_osaekomi_time >= 20) {
            sbState.white.osaekomi.running = false
            sbState.white.ippon = true
            sbState.white.wazaari_pending = false
            endOfTime(true)
        } else if (white_osaekomi_time >= 10 && !sbState.white.osaekomi.wazaari_given) {
            if (sbState.white.wazaari || sbState.white.wazaari_pending) {
                sbState.white.osaekomi.running = false
                sbState.white.wazaari_awasete_ippon = true
                sbState.white.wazaari_pending = false
                endOfTime(true)
            } else {
                sbState.white.wazaari_pending = true
                sbState.white.osaekomi.wazaari_given = true
            }
        }
    }

    if (sbState.blue.osaekomi.running) {
        blue_osaekomi_time = osaekomiTimeToSeconds(sbState.blue.osaekomi.since)

        if (blue_osaekomi_time >= 20) {
            sbState.blue.osaekomi.running = false
            sbState.blue.ippon = true
            sbState.blue.wazaari_pending = false
            endOfTime(true)
        } else if (blue_osaekomi_time >= 10 && !sbState.blue.osaekomi.wazaari_given) {
            if (sbState.blue.wazaari || sbState.blue.wazaari_pending) {
                sbState.blue.osaekomi.running = false
                sbState.blue.wazaari_awasete_ippon = true
                sbState.blue.wazaari_pending = false
                endOfTime(true)
            } else {
                sbState.blue.wazaari_pending = true
                sbState.blue.osaekomi.wazaari_given = true
            }
        }
    }
}

const determineWinner = (always) => {
    always ||= false;

    if (sbState.white.hansokumake && sbState.blue.hansokumake) {
        return false;
    } else if (sbState.blue.hansokumake) {
        return ['white', 10]
    } else if (sbState.white.hansokumake) {
        return ['blue', 10]
    }

    if (sbState.white.ippon && sbState.blue.ippon) {
        return false;
    } else if (sbState.white.ippon) {
        return ['white', 10]
    } else if (sbState.blue.ippon) {
        return ['blue', 10]
    }

    if (sbState.white.wazaari_awasete_ippon && sbState.blue.wazaari_awasete_ippon) {
        return false;
    } else if (sbState.white.wazaari_awasete_ippon) {
        return ['white', 10]
    } else if (sbState.blue.wazaari_awasete_ippon) {
        return ['blue', 10]
    }

    if (sbState.white.shido == 3 && sbState.blue.shido == 3) {
        return false;
    } else if (sbState.blue.shido == 3) {
        return ['white', 10]
    } else if (sbState.white.shido == 3) {
        return ['blue', 10]
    }

    if (!always) { return false; }

    if (sbState.white.wazaari && sbState.blue.wazaari) {
        return false;
    } else if (sbState.white.wazaari) {
        return ['white', 7]
    } else if (sbState.blue.wazaari) {
        return ['blue', 7]
    }

    return false;
}

const properIntegralConversion = (val) => {
    if (sbState.time.displayTimeDirection == -1)
        return Math.ceil(val)
    else
        return Math.floor(val)
}

const osaekomiTimeToSeconds = (val) => {
    return Math.floor((sbState.time.globalTick - val) / 1000)
}

const resetState = (config) => {
    sbState = makeState(config || sbState.config)
}