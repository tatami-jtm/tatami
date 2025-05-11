let createHelperWindow = () => {
    let hw = document.createElement("div")
    document.body.appendChild(hw)
    hw.innerText = "Helfer lädt…"
    hw.style.position = "fixed"
    hw.style.bottom = "0.5em"
    hw.style.right = "0.5em"
    hw.style.padding = "1em"
    hw.style.fontFamily = "Reddit Mono"
    hw.style.fontSize = "0.95em"
    hw.style.whiteSpace = "pre-wrap"
    hw.style.color = "white"
    hw.style.backgroundColor = "#36363a"
    hw.style.borderTop = "0.5em solid teal"
    hw.style.userSelect = "none"
    hw.style.width = "300px"
    hw.style.maxHeight = "70vh"
    hw.style.overflowY = "auto"

    return hw
}

let loadProximityData = () => {
    let seg = document.querySelector(".segmentation")
    let data = []

    for (const segChild of seg.childNodes) {
        // skip non-html elements
        if (segChild.nodeType != 1) continue

        if(segChild.classList.contains("segmentation-item")) {
            data.push({ "type": "item",
                "checkbox": segChild.querySelector("input[type=checkbox]"),
                "weight": Number.parseFloat(segChild.querySelector("strong").innerText) })
        } else if(segChild.classList.contains("segmentation-control")) {
            data.push({ "type": "control",
                "checkbox": segChild.querySelector("input[type=checkbox]") })
        }
    }

    data.push({ "type": "final" })

    return data
}

let updateHelperWindow = (hw, data) => {
    numberOfGroups = 0
    maxGroupUserCount = 0
    maxGroupWeightDiff = 0
    maxGroupWeightDiffPerc = 0
    ignoredItems = 0

    groupData = []

    currentGroupUserCount = 0
    currentGroupInitialWeight = null
    lastWeight = 0

    for (const element of data) {
        if ((element.type == "control" && element.checkbox.checked) || element.type == "final") {
            if ((lastWeight - currentGroupInitialWeight) > maxGroupWeightDiff)
                maxGroupWeightDiff = lastWeight - currentGroupInitialWeight

            if ((lastWeight / currentGroupInitialWeight) > maxGroupWeightDiffPerc)
                maxGroupWeightDiffPerc = lastWeight / currentGroupInitialWeight

            if (currentGroupUserCount > maxGroupUserCount)
                maxGroupUserCount = currentGroupUserCount

            groupData.push([lastWeight, currentGroupUserCount])

            numberOfGroups++
            currentGroupUserCount = 0
            currentGroupInitialWeight = null
            lastWeight = 0
        } else if (element.type == "item") {
            if (!element.checkbox.checked) {
                ignoredItems++
                continue
            }

            currentGroupUserCount++
            lastWeight = element.weight

            if (currentGroupInitialWeight === null)
                currentGroupInitialWeight = element.weight
        }
    }

    maxGroupWeightDiff = maxGroupWeightDiff.toFixed(1)
    maxGroupWeightDiffPerc = ((maxGroupWeightDiffPerc - 1.0) * 100).toFixed(1)

    groupDataString = "Gruppen:\n"
    i = 0

    for (const group of groupData) {
        groupDataString += ("" + (++i)).padStart(2) + ") -" + group[0].toFixed(1) + " kg - " + (""+group[1]).padStart(2) + " TN\n"
    }
    
    groupDataString = groupDataString.trim()

    hw.innerText = ("Anzahl der Gruppen:  " + String(numberOfGroups).padStart(4) + "\n" +
                    "Max. Gruppengröße:   " + String(maxGroupUserCount).padStart(4) + " TN\n" +
                    "Übersprungene TN:    " + String(ignoredItems).padStart(4) + " TN\n" +
                    "Max. Differenz (kg): " + String(maxGroupWeightDiff).padStart(4) + " kg\n" +
                    "Max. Differenz (%):  " + String(maxGroupWeightDiffPerc).padStart(4) + " %\n\n") + groupDataString
}

window.addEventListener("load", () => {
    let hw = createHelperWindow()
    let data = loadProximityData()

    window.setInterval(updateHelperWindow, 500, hw, data)
})