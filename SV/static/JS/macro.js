
function plotGraph(graphID, jsonData) {
    // update the plot, .react is recommended for updating existing plot as it's more efficient than .newPlot
    Plotly.react(graphID, jsonData, { autosize: true });
}



function fetchTreeMapData(apiURL, graphID) {


    $.ajax({
        type: 'GET',
        url: apiURL,
        data: null,
        /*
        beforeSend: function () {
            console.log("starting spinner")
            $("#" + spinnerID).addClass("spinner-border");
            $("#" + refreshBtnID).hide();
        },*/
        success: function (response) {
            console.log("response received from server");
            plotGraph(graphID, JSON.parse(response));
            console.log("ploting tree map");
            // $("#"+tsID).text(getTS());
        },
        error: function (textStatus, errorThrown) {
            // createToast(graphID, textStatus, errorThrown);
            console.log("Error:", graphID, textStatus, errorThrown);
        }/*,
        complete: function () {
            $("#" + spinnerID).removeClass("spinner-border");
            $("#" + refreshBtnID).show();
        }*/
    }); //close ajax
}



function fetchSectorEvolsJsonData() {
    console.log("sending request for > treeMap < to server");
    fetchTreeMapData(`/api/fetchTreeMapJsonData`, "sectorEvolsTreeMap")
}


Plotly.newPlot("sectorEvolsTreeMap", null, { autosize: true }, { responsive: true }); // Graph 2
fetchSectorEvolsJsonData()