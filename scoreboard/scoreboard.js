// Initialize audio
const alert_audio = new Audio('alert.mp3');
alert_audio.loop = true;
alert_audio.playsinline = true;
alert_audio.load();

const properties = {
    "tatami-scoreboard:view": {
        changed: (prop) => {
            document.querySelector(".view.view-active")?.classList?.remove("view-active");
            document.querySelector(".view[data-sbf-view=\'" + prop + "\']")?.classList?.add("view-active");
        }
    },
    "tatami-scoreboard:white:name+club": {
        depends_on: [
            "tatami-scoreboard:white:name",
            "tatami-scoreboard:white:club"
        ],
        complex_render: (props) => {
            if (!props["tatami-scoreboard:white:club"])
                return props["tatami-scoreboard:white:name"];

            return props["tatami-scoreboard:white:name"] + " (" + props["tatami-scoreboard:white:club"] + ")"
        }
    },
    "tatami-scoreboard:blue:name+club": {
        depends_on: [
            "tatami-scoreboard:blue:name",
            "tatami-scoreboard:blue:club"
        ],
        complex_render: (props) => {
            if (!props["tatami-scoreboard:blue:club"])
                return props["tatami-scoreboard:blue:name"];

            return props["tatami-scoreboard:blue:name"] + " (" + props["tatami-scoreboard:blue:club"] + ")"
        }
    },
    "tatami-scoreboard:prepare:white:name+club": {
        depends_on: [
            "tatami-scoreboard:prepare:white:name",
            "tatami-scoreboard:prepare:white:club"
        ],
        complex_render: (props) => {
            if (!props["tatami-scoreboard:prepare:white:club"])
                return props["tatami-scoreboard:prepare:white:name"];

            return props["tatami-scoreboard:prepare:white:name"] + " (" + props["tatami-scoreboard:prepare:white:club"] + ")"
        }
    },
    "tatami-scoreboard:prepare:blue:name+club": {
        depends_on: [
            "tatami-scoreboard:prepare:blue:name",
            "tatami-scoreboard:prepare:blue:club"
        ],
        complex_render: (props) => {
            if(!props["tatami-scoreboard:prepare:blue:club"])
                return props["tatami-scoreboard:prepare:blue:name"];

            return props["tatami-scoreboard:prepare:blue:name"] + " (" + props["tatami-scoreboard:prepare:blue:club"] + ")"
        }
    },
    "tatami-scoreboard:mat-number": null,
    "tatami-scoreboard:class": null,
    "tatami-scoreboard:progress": null,
    "tatami-scoreboard:white:name": null,
    "tatami-scoreboard:white:club": null,
    "tatami-scoreboard:white:ippon": {
        render: (prop) => {
            return (prop == "1") ? 'IPPON' : ''
        }
    },
    "tatami-scoreboard:white:wazaari": {
        changed: (prop) => {
            wazaari = document.querySelector("[data-sbf-id='tatami-scoreboard:white:wazaari']");
            wazaari.classList.remove("active");
            wazaari.classList.remove("pending");

            if (prop == 'active')
                wazaari.classList.add("active");
            else if (prop == 'pending')
                wazaari.classList.add("pending");
        }
    },
    "tatami-scoreboard:prepare:white:shido+hansokumake": {
        depends_on: [
            "tatami-scoreboard:white:shido",
            "tatami-scoreboard:white:hansokumake"
        ],
        complex_changed: (props) => {
            let scope = document.querySelector("[data-sbf-id='tatami-scoreboard:white:shido+hansokumake']");
            
            has_shido_1 = parseInt(props["tatami-scoreboard:white:shido"]) >= 1;
            has_shido_2 = parseInt(props["tatami-scoreboard:white:shido"]) >= 2;
            has_hansokumake = parseInt(props["tatami-scoreboard:white:shido"]) == 3 || parseInt(props["tatami-scoreboard:white:hansokumake"]) == 1;
            
            if (has_shido_1)
                scope.querySelector('.card-shido:nth-of-type(1)').classList.remove('hidden');
            else
                scope.querySelector('.card-shido:nth-of-type(1)').classList.add('hidden');
    
            if (has_shido_2)
                scope.querySelector('.card-shido:nth-of-type(2)').classList.remove('hidden');
            else
                scope.querySelector('.card-shido:nth-of-type(2)').classList.add('hidden');
    
            if (has_hansokumake)
                scope.querySelector('.card-hansokumake').classList.remove('hidden');
            else
                scope.querySelector('.card-hansokumake').classList.add('hidden');
        }
    },
    "tatami-scoreboard:white:shido": null,
    "tatami-scoreboard:white:hansokumake": null,
    "tatami-scoreboard:blue:name": null,
    "tatami-scoreboard:blue:club": null,
    "tatami-scoreboard:blue:ippon": {
        render: (prop) => {
            return (prop == "1") ? 'IPPON' : ''
        }
    },
    "tatami-scoreboard:blue:wazaari": {
        changed: (prop) => {
            wazaari = document.querySelector("[data-sbf-id='tatami-scoreboard:blue:wazaari']");
            wazaari.classList.remove("active");
            wazaari.classList.remove("pending");

            if (prop == 'active')
                wazaari.classList.add("active");
            else if (prop == 'pending')
                wazaari.classList.add("pending");
        }
    },
    "tatami-scoreboard:prepare:blue:shido+hansokumake": {
        depends_on: [
            "tatami-scoreboard:blue:shido",
            "tatami-scoreboard:blue:hansokumake"
        ],
        complex_changed: (props) => {
            let scope = document.querySelector("[data-sbf-id='tatami-scoreboard:blue:shido+hansokumake']");
            
            has_shido_1 = parseInt(props["tatami-scoreboard:blue:shido"]) >= 1;
            has_shido_2 = parseInt(props["tatami-scoreboard:blue:shido"]) >= 2;
            has_hansokumake = parseInt(props["tatami-scoreboard:blue:shido"]) == 3 || parseInt(props["tatami-scoreboard:blue:hansokumake"]) == 1;
            
            if (has_shido_1)
                scope.querySelector('.card-shido:nth-of-type(1)').classList.remove('hidden');
            else
                scope.querySelector('.card-shido:nth-of-type(1)').classList.add('hidden');
    
            if (has_shido_2)
                scope.querySelector('.card-shido:nth-of-type(2)').classList.remove('hidden');
            else
                scope.querySelector('.card-shido:nth-of-type(2)').classList.add('hidden');
    
            if (has_hansokumake)
                scope.querySelector('.card-hansokumake').classList.remove('hidden');
            else
                scope.querySelector('.card-hansokumake').classList.add('hidden');
        }
    },
    "tatami-scoreboard:blue:shido": null,
    "tatami-scoreboard:blue:hansokumake": null,
    "tatami-scoreboard:time:running": {
        changed: (prop) => {
            if (prop != "false")
                document.querySelector("[data-sbf-id='tatami-scoreboard:time:running']").classList.add('running');
            else
                document.querySelector("[data-sbf-id='tatami-scoreboard:time:running']").classList.remove('running');
        }
    },
    "tatami-scoreboard:time:main": {
        render: (prop) => {
            return new Date(1000 * prop).toISOString().substr(15, 4)
        }
    },
    "tatami-scoreboard:time:golden-score": {
        render: (prop) => {
            return (prop != "false") ? 'Golden Score' : ''
        }
    },
    "tatami-scoreboard:time:osaekomi:white": {
        render: (prop) => {
            if (prop == null || prop == "-1") return '';
            
            prop = parseInt(prop);
            if (prop < 10) return '0' + String(prop);
            else return String(prop);
        }
    },
    "tatami-scoreboard:time:osaekomi:blue": {
        render: (prop) => {
            if (prop == null || prop == "-1") return '';

            prop = parseInt(prop);
            if (prop < 10) return '0' + String(prop);
            else return prop;
        }
    },
    "tatami-scoreboard:prepare:class": null,
    "tatami-scoreboard:prepare:white:name": null,
    "tatami-scoreboard:prepare:white:club": null,
    "tatami-scoreboard:prepare:blue:name": null,
    "tatami-scoreboard:prepare:blue:club": null,
    "tatami-scoreboard:time:flash-medical": {
        changed: (prop) => {
            if (prop != "false")
                document.querySelector("[data-sbf-id='tatami-scoreboard:time:flash']").classList.add('flashing-medical');
            else
                document.querySelector("[data-sbf-id='tatami-scoreboard:time:flash']").classList.remove('flashing-medical');
        }
    },
    "tatami-scoreboard:time:flash-alert": {
        changed: (prop) => {
            if (prop != "false") {
                document.querySelector("[data-sbf-id='tatami-scoreboard:time:flash']").classList.add('flashing-alert');
                alert_audio.play();
            }
            else {
                document.querySelector("[data-sbf-id='tatami-scoreboard:time:flash']").classList.remove('flashing-alert');
                alert_audio.pause();
                alert_audio.load();
            }
        }
    }
}

const defaults = {
    "tatami-scoreboard:view": 'break',
    "tatami-scoreboard:mat-number": 'Matte 1',
    "tatami-scoreboard:class": 'M+100kg',
    "tatami-scoreboard:progress": 'Hauptrunde',
    "tatami-scoreboard:white:name": 'AAAAA1',
    "tatami-scoreboard:white:club": 'A1-Verein',
    "tatami-scoreboard:white:ippon": "0",
    "tatami-scoreboard:white:wazaari": "0",
    "tatami-scoreboard:white:shido": "0",
    "tatami-scoreboard:white:hansokumake": "0",
    "tatami-scoreboard:blue:name": 'BBBBB1',
    "tatami-scoreboard:blue:club": 'B1-Verein',
    "tatami-scoreboard:blue:ippon": "0",
    "tatami-scoreboard:blue:wazaari": "0",
    "tatami-scoreboard:blue:shido": "0",
    "tatami-scoreboard:blue:hansokumake": "0",
    "tatami-scoreboard:time:runnning": "false",
    "tatami-scoreboard:time:main": "240",
    "tatami-scoreboard:time:golden-score": "false",
    "tatami-scoreboard:time:osaekomi:white": null,
    "tatami-scoreboard:time:osaekomi:blue": null,
    "tatami-scoreboard:prepare:class": 'M+100kg',
    "tatami-scoreboard:prepare:white:name": 'AAAAA2',
    "tatami-scoreboard:prepare:white:club": 'A2-Verein',
    "tatami-scoreboard:prepare:blue:name": 'BBBBB2',
    "tatami-scoreboard:prepare:blue:club": 'B2-Verein',
    "tatami-scoreboard:flash-medical": "false",
    "tatami-scoreboard:flash-alert": "false"
}

let current_values = { "tatami-scoreboard:view": '-' };

let update = () => {

    if (localStorage.getItem("tatami-scoreboard:reset") == "true") return reset();

    for (const prop in properties) {
        const propopts = properties[prop];

        if (propopts == null || 'render' in propopts) {
            let propval = localStorage.getItem(prop);
            if (propval == undefined)
                propval = defaults[prop];

            let propchanged = (propval != current_values[prop]);
            current_values[prop] = propval;

            if (propchanged) {
                if (propopts != null) {
                    propval = propopts.render(propval)
                }
    
                let holders = document.querySelectorAll("[data-sbf=\'" + prop + "\']")
                for (const hol of holders) {
                    hol.innerText = propval;
                }
            }
        } else if ('complex_render' in propopts) {
            let dep_props = {};
            let propchanged = false;

            
            for (const dep_prop_candidate of propopts.depends_on) {
                let propval = localStorage.getItem(dep_prop_candidate);
                if (propval == undefined)
                    propval = defaults[dep_prop_candidate];
                
                propchanged = propchanged || (propval != current_values[dep_prop_candidate]);
                dep_props[dep_prop_candidate] = propval;
            }
            
            if (propchanged) {
                propval = propopts.complex_render(dep_props);
    
                let holders = document.querySelectorAll("[data-sbf=\'" + prop + "\']")
                for (const hol of holders) {
                    hol.innerText = propval;
                }
            }
        } else if ('changed' in propopts) {
            let propval = localStorage.getItem(prop);
            if (propval == undefined)
                propval = defaults[prop];

            propchanged = (propval != current_values[prop]);
            current_values[prop] = propval;

            if (propchanged) {
                propopts.changed(propval)
            }
        } else if ('complex_changed' in propopts) {
            let dep_props = {};
            let propchanged = false;

            
            for (const dep_prop_candidate of propopts.depends_on) {
                let propval = localStorage.getItem(dep_prop_candidate);
                if (propval == undefined)
                    propval = defaults[dep_prop_candidate];
                
                propchanged = propchanged || (propval != current_values[dep_prop_candidate]);
                dep_props[dep_prop_candidate] = propval;
            }

            if (propchanged) {
                propopts.complex_changed(dep_props)
            }
        }
    }
};

let reset = () => {
    for (const prop in properties) {
        localStorage.removeItem(prop);
    }

    current_values = { "tatami-scoreboard:view": '-' }
    localStorage.removeItem("tatami-scoreboard:reset");

    console.log("TOTAL RESET done");
};

setInterval(update, 50);

document.body.addEventListener("click", (e) => {
    document.body.parentNode.classList.add('active');
})