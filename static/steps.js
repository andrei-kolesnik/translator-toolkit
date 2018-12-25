$(document).ready(function() {
    $("body").on("click", ".file", function(e) {
        var filename = $(e.target).text();
        $.getJSON("/step2/" + filename, function(result) {
            var div = document.getElementById('raw');
            div.innerHTML = result;
            // div.appendChild(document.createTextNode(result));
        });
    });

    $("#tokens").click(function () {
        $.getJSON("/step3", function (result) {
            var tbl = document.createElement('table');
            tbl.setAttribute('class', "basic");
            $.each(result, function (i, field) {
                var tr = tbl.insertRow();
                var td1 = tr.insertCell();
                var td2 = tr.insertCell();
                var td3 = tr.insertCell();
                td1.setAttribute('class', "left");
                td2.setAttribute('class', "left");
                td3.setAttribute('class', "left");
                td1.appendChild(document.createTextNode(field.stem));
                td2.appendChild(document.createTextNode(field.count));
                td3.appendChild(document.createTextNode(field.words));
            });
            var div = document.getElementById('words');
            div.innerHTML = '';
            div.appendChild(tbl);
        });
    });
});
