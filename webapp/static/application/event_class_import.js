document.querySelector("[data-event_class-call]").addEventListener("click", async (e) => {
    let template_id = document.querySelector("[data-event_class-template]").value;

    if(!template_id) return;  // if we have not selected any, i.e. empty first element

    e.target.setAttribute("disabled", "disabled")
    e.target.classList.add("active")

    let response = await fetch("/admin/template/event_class/" + template_id)

    if(!response.ok) {
        alert("Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.")

        e.target.removeAttribute("disabled")
        e.target.classList.remove("active")

        return;
    }

    let data = await response.json()

    console.log(data)
    
    if (!document.getElementById("name").value) {
        document.getElementById("name").value = data.title
    }

    document.getElementById("short_name").value = data.short_title

    if (data.use_proximity_weight_mode)
        document.getElementById("weight_mode-proximity").checked = true
    else
        document.getElementById("weight_mode-predefined").checked = true

    document.getElementById("weight_generator").value = data.weight_generator.join("\n")

    document.getElementById("default_maximal_proximity").value = data.default_maximal_proximity
    document.getElementById("default_maximal_size").value = data.default_maximal_size

    document.getElementById("fighting_time").value = data.fighting_time
    document.getElementById("golden_score_time").value = data.golden_score_time
    document.getElementById("between_fights_time").value = data.between_fights_time

    e.target.removeAttribute("disabled")
    e.target.classList.remove("active")
});