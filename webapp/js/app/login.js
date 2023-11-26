function login_prototype(){}

login_prototype.trylogin = async (event) => {
    event.preventDefault();
    if(document.getElementById("trigger_fun_trylogin").reportValidity()) {
        login_name = document.getElementsByName('email-username')[0].value;
        password = document.getElementsByName('password')[0].value;

        api_prototype.api_call('GET', '/users/token', null, login_prototype.login_succ, login_prototype.login_fail, [login_name, password]);
    }

    setTimeout(() => {
        document.getElementsByName('password')[0].reportValidity();
    }, 500);
};

login_prototype.login_succ = (route, json) => {
    console.log("Login success!");
    console.log(json);
    app_state['user'] = {
        ...json
    };
    app_state['logged_in'] = true;
    setCookie('user', JSON.stringify(json));

    document.getElementById('profile_badge').innerHTML = '<span class="fw-semibold d-block">' + json['name'] + '</span><small class="text-muted">' + json['email'] + '</small>';

    if(window.location.hash != '') {
        let location_hash = window.location.hash;

        nav_prototype.open_page(location_hash.split('#')[1]);
    } else {
        nav_prototype.open_page('stats');
    }
};

login_prototype.login_fail = () => {
    document.getElementById("trigger_fun_trylogin").insertAdjacentHTML('beforeend',
        '<div class="alert alert-danger alert-dismissible" role="alert"> \
            User or Password invalid! \
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button> \
        </div>');
};

login_prototype.logout = async () => {
    app_state['user'] = null;
    app_state['logged_in'] = false;
    setCookie('user', '');

    location.reload();
};

login_prototype.open_profile = (elem) => {
    // First open users page and then open edit box for current logged in user

    nav_prototype.open_page('users', () => {
        nav_prototype.curr_page_singular = 'profile';
        nav_prototype.curr_page_elem = app_state['user'].id;
        view_prototype.load_edit(null);
    });
};

// Initialization methods
document.getElementById("trigger_fun_trylogin").addEventListener("submit", login_prototype.trylogin, false);
document.getElementById("btn_logout").addEventListener("click", login_prototype.logout, false);


document.addEventListener("DOMContentLoaded", function(){
    if(getCookie('user') != '' && getCookie('user') != 'undefined') {
        login_prototype.login_succ('/users/token', JSON.parse(getCookie('user')));
    }
});