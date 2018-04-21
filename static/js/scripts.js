function tshirt() {
    var ss = document.getElementById("Small Stock");
    var ms = document.getElementById("Medium Stock");
    var ls = document.getElementById("Large Stock");
    var stock = document.getElementById("Stock");

    stock.style.display = ("none");
    ss.style.display = ("inline");
    ms.style.display = ("inline");
    ls.style.display = ("inline");

    stock.value = 0;
    ss.value = "";
    ms.value = "";
    ls.value = "";
}

function other() {
    var ss = document.getElementById("Small Stock");
    var ms = document.getElementById("Medium Stock");
    var ls = document.getElementById("Large Stock");
    var stock = document.getElementById("Stock");

    stock.style.display = ("inline");
    ss.style.display = ("none");
    ms.style.display = ("none");
    ls.style.display = ("none");

    stock.value = "";
    ss.value = 0;
    ms.value = 0;
    ls.value = 0;

}