var local_config = {
    fightDuration: 240,
    hasGoldenScore: true,
    maxGoldenScore: null,
    defaultScreen: 'main'
}

const class_ = document.querySelector("[data-control=\"class\"]")
const progress = document.querySelector("[data-control=\"progress\"]")
const white_name = document.querySelector("[data-control=\"white.name\"]")
const white_club = document.querySelector("[data-control=\"white.club\"]")
const blue_name = document.querySelector("[data-control=\"blue.name\"]")
const blue_club = document.querySelector("[data-control=\"blue.club\"]")

const prepare_class = document.querySelector("[data-control=\"prepare.class\"]")
const prepare_progress = document.querySelector("[data-control=\"prepare.progress\"]")
const prepare_white_name = document.querySelector("[data-control=\"prepare.white.name\"]")
const prepare_white_club = document.querySelector("[data-control=\"prepare.white.club\"]")
const prepare_blue_name = document.querySelector("[data-control=\"prepare.blue.name\"]")
const prepare_blue_club = document.querySelector("[data-control=\"prepare.blue.club\"]")

const prepare_goto = document.querySelector("[data-control=\"prepare.goto\"]")

const config_fighting_time = document.querySelector("[data-control=\"config.fighting_time\"]")
const config_golden_score_time = document.querySelector("[data-control=\"config.golden_score_time\"]")

const standaloneTick = () => {
    setOption("class", class_.value)
    setOption("progress", progress.value)
    setOption("white:name", white_name.value)
    setOption("white:club", white_club.value)
    setOption("blue:name", blue_name.value)
    setOption("blue:club", blue_club.value)

    setOption("prepare:class", prepare_class.value)
    setOption("prepare:white:name", prepare_white_name.value)
    setOption("prepare:white:club", prepare_white_club.value)
    setOption("prepare:blue:name", prepare_blue_name.value)
    setOption("prepare:blue:club", prepare_blue_club.value)

    local_config.fightDuration = parseInt(config_fighting_time.value)
    let gs_value = parseInt(config_golden_score_time.value)

    if (gs_value == -1) {
        local_config.hasGoldenScore = true
        local_config.maxGoldenScore = null
    } else if (gs_value == 0) {
        local_config.hasGoldenScore = false
        local_config.maxGoldenScore = null
    } else {
        local_config.hasGoldenScore = true
        local_config.maxGoldenScore = gs_value
    }
}

prepare_goto.addEventListener("click", () => {
    class_.value = prepare_class.value
    progress.value = prepare_progress.value
    white_name.value = prepare_white_name.value
    white_club.value = prepare_white_club.value
    blue_name.value = prepare_blue_name.value
    blue_club.value = prepare_blue_club.value

    prepare_class.value = ""
    prepare_white_name.value = ""
    prepare_white_club.value = ""
    prepare_blue_name.value = ""
    prepare_blue_club.value = ""

    resetState(local_config)
})

window.addEventListener("load", () => {
    setInterval(standaloneTick, 50)
})