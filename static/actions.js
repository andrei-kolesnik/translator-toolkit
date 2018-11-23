$(document).ready(function() {
    $("#freq").click(function() {
        $.getJSON("/freq", function(result) {
            var tbl = document.createElement('table');
            tbl.setAttribute('class', "basic");
            $.each(result, function(i, field) {
                var tr = tbl.insertRow();
                var td1 = tr.insertCell(); 
                var td2 = tr.insertCell(); 
                td1.setAttribute('class', "left");
                td2.setAttribute('class', "right");
                td1.innerHTML = "<a href=\"#\" class=\"word\" onclick=\"concordance('"+field[0]+"', "+field[1]+')">'+field[0]+'</a>';
                td2.appendChild(document.createTextNode(field[1]));
            });
            var div = document.getElementById('left1');
            div.innerHTML = '';
            div.appendChild(tbl);
        });
    });
/*
    $("body").on("click", ".word", function(e) {
        var word = $(e.target).text();
        $.getJSON("/concordance/"+word, function(result) {
            var tbl = document.createElement('table');
            tbl.setAttribute('class', "concordance");
            $.each(result, function(i, field) {
                var tr = tbl.insertRow();
                var td1 = tr.insertCell(); 
                var td2 = tr.insertCell(); 
                var td3 = tr.insertCell(); 
                td1.setAttribute('class', "right");
                td2.setAttribute('class', "center");
                td3.setAttribute('class', "left");
                td1.appendChild(document.createTextNode(field.left_print));
                td2.appendChild(document.createTextNode(field.query));
                td3.appendChild(document.createTextNode(field.right_print));
            });
            var div = document.getElementById('concordance_div');
            div.innerHTML = '';
            div.appendChild(tbl);
        });
    });
*/    
});

function concordance(word, count) {
    $.getJSON("/contexts/"+word, function(result) {
        var tbl = document.createElement('table');
        tbl.setAttribute('class', "basic");
        $.each(result, function(i, field) {
            var tr = tbl.insertRow();
            var td1 = tr.insertCell(); 
            var td2 = tr.insertCell(); 
            var td3 = tr.insertCell(); 
            td1.setAttribute('class', "right");
            td2.setAttribute('class', "center");
            td3.setAttribute('class', "left");
            td1.appendChild(document.createTextNode(field.left_print));
            td2.appendChild(document.createTextNode(field.query));
            td3.appendChild(document.createTextNode(field.right_print));
        });
        var div = document.getElementById('right1');
        div.innerHTML = '<b>All Concordance:</b>';
        div.appendChild(tbl);
    });
    $.getJSON("/concordance/"+word+"/"+count, function(result) {
        var tbl = document.createElement('table');
        tbl.setAttribute('class', "basic");
        $.each(result, function(i, field) {
            var tr = tbl.insertRow();
            var td1 = tr.insertCell(); 
            var td2 = tr.insertCell(); 
            var td3 = tr.insertCell(); 
            td1.setAttribute('class', "right");
            td2.setAttribute('class', "center");
            td3.setAttribute('class', "left");
            td1.appendChild(document.createTextNode(field.left_print));
            td2.appendChild(document.createTextNode(field.query));
            td3.appendChild(document.createTextNode(field.right_print));
        });
        var div = document.getElementById('right2');
        div.innerHTML = '<b>Unique Contexts:</b>';
        div.appendChild(tbl);
    });
}
