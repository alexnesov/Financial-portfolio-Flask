
$(document).ready(function() {
    $('#example').DataTable();

    const selectElement = document.querySelector('#example_length');
    console.log("selectElement: ", selectElement);

    selectElement.addEventListener('change', (event) => {

        var sector_perf_content = document.getElementById("sector_perf");
        sector_perf_content.style.maxHeight = sector_perf_content.scrollHeight + "px";

      });

} );

function plotGraph(graphID, jsonData) {
    // update the plot, .react is recommended for updating existing plot as it's more efficient than .newPlot
    Plotly.react(graphID, jsonData, { autosize: true });
}


// Gets all the collapsibles --> HTML collection
let coll = document.getElementsByClassName("collapsible");

let i = 0;

window.onload = ()=>{
let iniColl = document.querySelectorAll(".collapsible");
iniColl.forEach(function(c){
        c.classList.add("active");
        let iniCont = c.nextElementSibling;
        if (iniCont.style.maxHeight){
            iniCont.style.maxHeight = null;
        } else {
            iniCont.style.maxHeight = iniCont.scrollHeight + "px";
        } 
    });
};

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {

        this.classList.toggle("active");
        var content = this.nextElementSibling;

        if (content.style.maxHeight){
            content.style.maxHeight = null;
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
        } 
    });
}


function fetchTreeMapData(apiURL, graphID, spinnerID, interval) {
    $.ajax({
        type: 'GET',
        url: apiURL,
        data: null,
        beforeSend: function () {
            console.log("starting spinner")
            $("#" + spinnerID).show();
        },
        success: function (response) {
            console.log("response received from server");
            plotGraph(graphID, JSON.parse(response));
            console.log("ploting tree map");
            // $("#"+tsID).text(getTS());
        },
        error: function (textStatus, errorThrown) {
            // createToast(graphID, textStatus, errorThrown);
            console.log("Error:", graphID, textStatus, errorThrown);
        },
        complete: function () {
            $("#" + spinnerID).hide();
        }
    }); //close ajax
}



function fetchSectorEvolsJsonData(interval) {
    /**/
    console.log("sending request for > sectorEvols < to server");
    console.log(`Interval: `, interval)
    fetchTreeMapData(`/api/fetchSectorEvols?interval=${interval}`, "sectorEvolsTreeMap", "spinner", interval)
}


Plotly.newPlot("sectorEvolsTreeMap", null, { autosize: true }, { responsive: true }); // Graph 2
fetchSectorEvolsJsonData("Perf_1")