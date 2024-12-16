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
                scores_given: []
            },
            scores: {}
        },
        blue: {
            osaekomi: {
                running: false,
                since: null,
                scores_given: []
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
    let sides = ['white', 'blue']
    for (const side of sides) {
        if (sbState[side].osaekomi.running) {
            osaekomi_time = osaekomiTimeToSeconds(sbState[side].osaekomi.since)

            for (const osaekomi_rule of SBRULES.osaekomi) {
                if (osaekomi_time < osaekomi_rule.at)
                    continue
                if (sbState[side].osaekomi.scores_given.includes(osaekomi_rule.score))
                    continue
                if (sbState[side].scores[osaekomi_rule.score].value >= SBRULES.scores[osaekomi_rule.score].max_count)
                    continue

                sbState[side].scores[osaekomi_rule.score].value += 1
                sbState[side].scores[osaekomi_rule.score].pending = !osaekomi_rule.final
                sbState[side].osaekomi.scores_given.push(osaekomi_rule.score)

                if (sbState[side].osaekomi.scores_given.length > 1) {

                    let last_score = sbState[side].osaekomi.scores_given.at(-2)
                    sbState[side].scores[last_score].pending = false

                    if (sbState[side].scores[last_score].value > 0)
                        sbState[side].scores[last_score].value -= 1
                }

                if (osaekomi_rule.final) {
                    sbState[side].osaekomi.running = false
                    endOfTime(true)
                }
            }
        }
    }
}

const checkForAccumulation = () => {
    let sides = ['white', 'blue']
    for (const side of sides) {
        /* Step 1: set everything as if not-accumulated */
        for (const score_name in SBRULES.scores) {
            if (Object.prototype.hasOwnProperty.call(SBRULES.scores, score_name)) {
                sbState[side].scores[score_name].value_with_accum = 
                            sbState[side].scores[score_name].value;
            }
        }

        /* Calculate acumulations */
        for (const score_name in SBRULES.scores) {
            if (Object.prototype.hasOwnProperty.call(SBRULES.scores, score_name)) {
                const score = SBRULES.scores[score_name];

                if (!score.accumulates) continue

                let accumulates_to = score.accumulates;
                
                if ((sbState[side].scores[score_name].value == score.max_count) &&
                    (!sbState[side].scores[score_name].pending)) {

                    if(sbState[side].scores[accumulates_to].value < SBRULES.scores[accumulates_to].max_count) {
                        sbState[side].scores[accumulates_to].value_with_accum += 1;
                    }
                }
            }
        }
    }
}

const determineWinner = (always) => {
    always ||= false;

    for (const rank of SBRULES.ranking) {
        if (!always && !SBRULES.scores[rank].ends_fight) continue

        if (SBRULES.scores[rank].penalty) {
            if (sbState.white.scores[rank].value_with_accum > sbState.blue.scores[rank].value_with_accum)
                return ['blue', SBRULES.scores[rank].points]
            else if (sbState.white.scores[rank].value_with_accum < sbState.blue.scores[rank].value_with_accum)
                return ['white', SBRULES.scores[rank].points]
            else
                continue
        } else {
            if (sbState.white.scores[rank].value_with_accum > sbState.blue.scores[rank].value_with_accum)
                return ['white', SBRULES.scores[rank].points]
            else if (sbState.white.scores[rank].value_with_accum < sbState.blue.scores[rank].value_with_accum)
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