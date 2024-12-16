/* Model */

const makeState = (config) => {
    base = {
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
            scores: {}
        },
        blue: {
            osaekomi: {
                running: false,
                since: null,
                wazaari_given: false
            },
            scores: {}
        }
    }

    for (const score_name in SBRULES.scores) {
        if (Object.prototype.hasOwnProperty.call(SBRULES.scores, score_name)) {
            const score = SBRULES.scores[score_name];
            base.white.scores[score_name] = { value: 0, pending: false, from_osaekomi: false, value_with_accum: 0 }
            base.blue.scores[score_name] = { value: 0, pending: false, from_osaekomi: false, value_with_accum: 0 }
        }
    }

    return base
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

    checkForAccumulation()
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

const checkForAccumulation = () => {
    let sides = ['white', 'blue']
    for (const side of sides) {
        for (const score_name in SBRULES.scores) {
            if (Object.prototype.hasOwnProperty.call(SBRULES.scores, score_name)) {
                const score = SBRULES.scores[score_name];

                if (!score.accumulates) continue

                let accumulates_to = score.accumulates;
                
                if ((sbState[side].scores[score_name].value == score.max_count) &&
                    (!sbState[side].scores[score_name].pending)) {

                    if(sbState[side].scores[accumulates_to].value < SBRULES.scores[accumulates_to].max_count) {
                        sbState[side].scores[accumulates_to].value_with_accum = 
                            sbState[side].scores[accumulates_to].value + 1;
                    }
                } else {
                    sbState[side].scores[accumulates_to].value_with_accum = 
                            sbState[side].scores[accumulates_to].value;
                }
            }
        }
    }
}

const determineWinner = (always) => {
    always ||= false;

    for (const rank of SBRULES.ranking) {
        if (!always && !SBRULES.ends_fight) continue

        if (SBRULES.scores[rank].penalty) {
            if (sbState.white.score[rank].value_with_accum > sbState.blue.score[rank].value_with_accum)
                return ['blue', SBRULES.scores[rank].points]
            else if (sbState.white.score[rank].value_with_accum < sbState.blue.score[rank].value_with_accum)
                return ['white', SBRULES.scores[rank].points]
            else
                continue
        } else {
            if (sbState.white.score[rank].value_with_accum > sbState.blue.score[rank].value_with_accum)
                return ['white', SBRULES.scores[rank].points]
            else if (sbState.white.score[rank].value_with_accum < sbState.blue.score[rank].value_with_accum)
                return ['blue', SBRULES.scores[rank].points]
            else
                continue
        }
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