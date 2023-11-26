function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

String.prototype.ucwords = function() {
    str = this.toLowerCase();
    return str.replace(/(^([a-zA-Z\p{M}]))|([ -][a-zA-Z\p{M}])/g,
        function(s){
          return s.toUpperCase();
      });
};

String.prototype.beautify = function() {
    return this.replaceAll("_", " ").ucwords();
}

function isDict(v) {
    return typeof v==='object' && v!==null && !(v instanceof Array) && !(v instanceof Date);
}

function hex2a(hexx) {
    var hex = hexx.toString();//force conversion
    var str = '';
    for (var i = 0; i < hex.length; i += 2)
        str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
    return str;
}

function addLoadingSpinner(elem) {
    elem.innerHTML += '<div class="loading_spinner" style="display: table; width: 100%; position: relative;"> \
                        <div class="spinner-border spinner-border-lg text-primary" role="status" style="margin-left: calc(50% - 1.5rem); margin-top: 50px; margin-bottom: 50px;"> \
                            <span class="visually-hidden">Loading...</span> \
                        </div> \
                    </div>';
}

function addErrorNotification(error) {
    document.getElementById('error_spawner').insertAdjacentHTML('beforebegin',
                '<div class="alert alert-danger alert-dismissible" role="alert"> \
                    ' + error + ' \
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button> \
                </div>'
            );
}