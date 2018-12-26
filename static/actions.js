$(document).ready(function() {

    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });

    $('#sidebarCollapse').on('click', function () {
        // open or close navbar
        $('#sidebar, #content').toggleClass('active');
        // close dropdowns
        $('.collapse.in').toggleClass('in');
        // and also adjust aria-expanded attributes we use for the open/closed arrows
        // in our CSS
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });

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
//                td1.innerHTML = "<a href=\"#\" class=\"word\" onclick=\"concordance('"+field[0]+"', "+field[1]+')">'+field[0]+'</a>';
//                td1.innerHTML = '<a href="/s1/' + field[0] + '"' + " class=\"word\" onclick=\"concordance('" + field[0] + "', " + field[1] + ')">' + field[0] + '</a>';
//                td1.innerHTML = '<a href="/s1/' + encodeURIComponent(field.stem) + '"' + ' class="word">' + field.words + '</a>';
//                td1.innerHTML = '<a href="#" class="word" name="' + field.stem + '">' + field.words + '</a>';
                td1.innerHTML = "<a href=\"#\" class=\"word\" onclick=\"s3('" + field.stem + "', '" + field.words + "')\">" + field.words + '</a>';
                td2.appendChild(document.createTextNode(field.count));
            });
            $("#btn-words").removeClass("hid");
            var div = document.getElementById('left1');
            div.innerHTML = '';
            div.appendChild(tbl);
            $("#btn-words").click();
        });
    });

    $("#unusual").click(function () {
        $.getJSON("/unusual", function (result) {
            var tbl = document.createElement('table');
            tbl.setAttribute('class', "basic");
            $.each(result, function (i, field) {
                var tr = tbl.insertRow();
                var td1 = tr.insertCell();
                var td2 = tr.insertCell();
                td1.setAttribute('class', "left");
                td2.setAttribute('class', "right");
                td1.innerHTML = "<a href=\"#\" class=\"word\" onclick=\"s3('" + field.stem + "', '" + field.words + "')\">" + field.words + '</a>';
                td2.appendChild(document.createTextNode(field.count));
            });
            $("#btn-words").removeClass("hid");
            var div = document.getElementById('left3');
            div.innerHTML = '';
            div.appendChild(tbl);
            $("#btn-words").click();
        });
    });

    $("#collocations").click(function () {
        $.getJSON("/collocations", function (result) {
            var tbl = document.createElement('table');
            tbl.setAttribute('class', "basic");
            $.each(result, function (i, field) {
                var tr = tbl.insertRow();
                var td1 = tr.insertCell();
                td1.setAttribute('class', "left");
                td1.innerHTML = '<a href="/s1/' + encodeURIComponent(field.term) + '"' + ' class="word">' + field.term + '</a>';
            });
            $("#btn-collocations").removeClass("hid");
            var div = document.getElementById('left2');
            div.appendChild(tbl);
            $("#btn-collocations").click();
        });
    });
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
        var div = document.getElementById('right2');
        div.innerHTML = '<b>All Concordance:</b>';
        div.appendChild(tbl);
    });
}

function s3(stem, words) {
    $.getJSON("/s3/" + stem, function (result) {
        var tbl = document.createElement('table');
        tbl.setAttribute('class', "basic");
        $.each(result, function (i, field) {
            var tr = tbl.insertRow();
            var td1 = tr.insertCell();
            var td2 = tr.insertCell();
            td1.setAttribute('class', "center");
            td2.setAttribute('class', "left");
            td1.appendChild(document.createTextNode(field.index));
//            td2.appendChild(document.createTextNode(field.sent));
            td2.innerHTML = field.sent;
        });
        var div = document.getElementById('right2');
        div.innerHTML = '<b>' + words + '</b>';
        div.appendChild(tbl);
    });
}
