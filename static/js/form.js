


var myvalp = document.getElementById('petid');
myvalp.onchange=function () {

    alert("dd");

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
             alert(xhr.responseText);
        }
    }
    xhr.open("POST", "/updateauth");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ petval: myvalp }));


}





