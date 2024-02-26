document.addEventListener("DOMContentLoaded", function () {

    function abortBuild() {
        var logBox = document.getElementById("logBox");
        logBox.innerHTML = "<p>Aborting tests</p>";

        fetch('/abort_build', {
            method: 'POST',
        })
        .then(response => response.json());

        statusIntervalAbort = setInterval(updateConsole, 5000);
    }

    function runBuild() {
        var selectedVersion = document.getElementById("category_select").value;
        var inputMail = document.getElementById("inputMail").value;
        var platform = document.querySelector('input[name="safewalkRadio"]:checked').value;
        var devSwitch = document.getElementById("devSwitch").checked;
        var ocUi = document.getElementById("oc-ui").checked;
        var tntUi = document.getElementById("tnt-ui").checked;
        var authApi = document.getElementById("auth-api").checked;
        var authRadius = document.getElementById("auth-radius").checked;
        var postmanOc = document.getElementById("postman-oc").checked;
        var postmanTnt = document.getElementById("postman-tnt").checked;


        var anySwitchSelected = Array.from(otherSwitches).some(function (switchElement) {
            return switchElement.checked;
        });

        if (!isRunning && selectedVersion !== "" && anySwitchSelected) {
            var data = new FormData();
            data.append("selected_version", selectedVersion);
            data.append("inputMail", inputMail);
            data.append("platform", platform);
            data.append("devSwitch", devSwitch);
            data.append("ocUi", ocUi);
            data.append("tntUi", tntUi);
            data.append("authApi", authApi);
            data.append("authRadius", authRadius);
            data.append("postmanOc", postmanOc);
            data.append("postmanTnt", postmanTnt);

            fetch('/', {
                method: 'POST',
                body: data
            })
            .then(function (response) {
            if (response.ok) {
                var logBox = document.getElementById("logBox");
                logBox.innerHTML = "<p>Sending tests</p>";
                statusInterval = setInterval(waitUntilRunning, 5000);

                setTimeout(function(){
                    statusInterval = setInterval(updateConsole, 5000);
                }, 20000);
            } else {
              throw new Error("Error en la solicitud");
            }
            })
        } else {
            return false;
        }
    }

    document.getElementById("abortButton").addEventListener("click", abortBuild);
    document.getElementById("runButton").addEventListener("click", runBuild);

    var isRunning = false;
    var result = "";

    function updateStatus() {
        fetch('/get_task_status')
            .then(response => response.json())
            .then(data => {
                isRunning = data.isInProgress;
                return isRunning;
            });
    }

    function updateResult(){
        fetch('/get_task_result')
            .then(response => response.json())
            .then(data => {
                result = data.taskResult;
                return result;
            }
            );
    }

    function waitUntilRunning(){
        updateStatus();
        if (isRunning){
            clearInterval(statusInterval);
        }
    }

    function updateConsole(){
        updateStatus();

        var logBox = document.getElementById("logBox");
        if (isRunning) {
            logBox.innerHTML = "<p>Test are RUNNING</p>";

        }else{
            updateResult();
            if (result == "SUCCESS"){
                clearInterval(statusInterval);
                logBox.innerHTML = "<p>Test are FINISHED</p>";
            }else if (result == "ABORTED"){
                clearInterval(statusInterval);
                clearInterval(statusIntervalAbort);
                logBox.innerHTML = "<p>Test are ABORTED</p>";
            }
        }
        updateStatus();
    }

    // MANEJO DE SWITCHES
    var allSwitch = document.getElementById("allSwitch");
    var otherSwitches = document.querySelectorAll('.form-check-input:not(#allSwitch):not(#devSwitch)');
    var ocUiSwitch = document.getElementById("oc-ui");
    var postmanOcSwitch = document.getElementById("postman-oc");
    var mtRadio = document.getElementById("multitenancyPlatform");
    var v5Radio = document.getElementById("V5Platform");

    v5Radio.addEventListener("change", function () {
        if (v5Radio.checked) {
            ocUiSwitch.checked = false;
            ocUiSwitch.disabled = true;
            postmanOcSwitch.checked = false;
            postmanOcSwitch.disabled = true;
        } else {
            ocUiSwitch.disabled = false;
            postmanOcSwitch.disabled = false;
        }
    });

    mtRadio.addEventListener("change", function () {
        if (mtRadio.checked) {
            if (allSwitch.checked){
                ocUiSwitch.checked = true;
                postmanOcSwitch.checked = true;
            }else{
                ocUiSwitch.disabled = false;
                postmanOcSwitch.disabled = false;
            }
        }
    });

    otherSwitches.forEach(function (switchElement) {
        switchElement.checked = true;
        switchElement.disabled = true;
    });

    allSwitch.addEventListener("change", function () {
        var allChecked = allSwitch.checked;

        otherSwitches.forEach(function (switchElement) {
            switchElement.checked = allChecked;
        });

        otherSwitches.forEach(function (switchElement) {
            switchElement.disabled = allChecked;
        });

        if (v5Radio.checked) {
            ocUiSwitch.checked = false;
            ocUiSwitch.disabled = true;
            postmanOcSwitch.checked = false;
            postmanOcSwitch.disabled = true;
        }
    });

    otherSwitches.forEach(function (switchElement) {
        switchElement.addEventListener("change", function () {
            var allChecked = Array.from(otherSwitches).every(function (switchElement) {
                return switchElement.checked;
            });

            allSwitch.checked = allChecked;
        });
    });
// FIN MANEJO DE SWITCHES


    var statusInterval;

    updateStatus();

});