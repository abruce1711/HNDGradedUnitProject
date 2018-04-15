function hideSize() {
    var size = document.getElementById("Size");
    size.style.display=("none");
    var option = document.createElement("option");
    option.text = "no_size";
    option.value = "no_size";
    size.add(option, size[0]);
    size.selectedIndex = 0;
}

function showSize() {
    var size = document.getElementById("Size");
    size.style.display=("inline");
    var remove =  size.length-4;
    for(var i=0; i<remove;i++) {
        size.selectedIndex = 0;
        size.remove(0);
    }
}