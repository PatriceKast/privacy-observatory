function nav_prototype() { }

nav_prototype.curr_page = null;
nav_prototype.curr_page_group = null;
nav_prototype.curr_page_elem = null;

// just stylistic variabls
nav_prototype.curr_page_singular = null;
nav_prototype.curr_page_title = null;

nav_prototype.open_page = (page, callback=null, push_browserstate = true) => {
    console.log("Try to open " + page);
    if(nav_prototype.curr_page == page) {
        callback();
        return;
    }
    nav_prototype.curr_page = page;

    // set url
    if(push_browserstate) {
        history.pushState(null, "", '#' + page);
    }

    // separate the obj_name from the page string
    [nav_prototype.curr_page_group, nav_prototype.curr_page_elem] = page.split("/");
    nav_prototype.curr_page_singular = nav_prototype.curr_page_group.slice(0, -1);

    // hide Login Window
    document.getElementById('wrapper_login').style.display = 'none';
    document.getElementById('wrapper_general').style.display = 'unset';

    // Handle Side Menu
    [].forEach.call(document.getElementsByClassName("menu-link"), function (element) {
        element.parentElement.classList.remove("active");
    });

    document.getElementById('menu_' + nav_prototype.curr_page_group).parentElement.classList.add('active');
    // if its a dropdown, also set parent holder to active
    let grandParentElem = document.getElementById('menu_' + nav_prototype.curr_page_group).parentElement.parentElement.parentElement;
    if(grandParentElem.classList.contains('menu-item')) {
        grandParentElem.classList.add('active');
    }

    // Handle Content
    view_prototype.load_view(callback);
};

nav_prototype.item_click = (e) => {
    if(e.target.id && e.target.id != '') {
        let req_page = e.srcElement.id.split("_")[1];
        nav_prototype.open_page(req_page);
    }
};

// attach an onclick listener for each menu item
[].forEach.call(document.getElementsByClassName("menu-link"), function (element) {
    element.addEventListener("click", nav_prototype.item_click, false);
});

// listen for backwards navigation of browser
window.addEventListener('popstate', function() {
    nav_prototype.open_page(window.location.hash.split('#')[1], null, false);
});