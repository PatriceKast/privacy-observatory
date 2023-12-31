function view_prototype(){}
view_prototype.static_settings = {
    'domainsets': {
        'adding': true,
        'editing': true,
        'text': 'Domaingenerators delivers the input to studies performed on the platform. These can either contain static domain lists or python3 code, which gets executed on the platform using the <span style="font-family: monospace;">eval()</span> functions.',
        'fields': {
            'name': {},
            'generator': {
                'multiline': true,
            },
        }
    },
    'studys': {
        'adding': true,
        'editing': true,
        'text': 'Studies can be registered on the platform using a cronjob styled schedule and prepared docker images and a docker compose file, which maps predefined input files and output files to the correct location within the study.<br><br>An example of this docker compose file is shown below:<pre>version: "3.4"\nservices:\n  anymip:\n    image: patcas/prvobs:anymip\n    volumes:\n      - /opt/input.txt:/opt/anymip/input.txt\n      - /opt/output.txt:/opt/anymip/output.txt</pre>The following conjob schedules can be handy:<pre>weekly:\t\t0 0 * * 0\nmonthly:\t0 0 1 * *\nquarterly:\t0 0 1 */3 *\nbiannually:\t0 0 1 */6 *\nyearly:\t\t0 0 1 1 *</pre><br><br>By selecting a specific worker_id for a study, a specific execution environment can be installed (e.g. VPN networks), which can then be used throughout the study performance.',
        'fields': {
            'name': {},
            'author': {},
            'cron_schedule': {},
            'domainset_id': {},
            'worker_id': {},
            'composefile': {
                'multiline': true,
            },
            'output_format': {
                'multiline': true,
            },
        }
    },
    'domains': {
        'adding': true,
        'editing': true,
        'text': 'This is HTML text for Domains',
        'fields': {
        }
    },
    'workers': {
        'adding': true,
        'editing': true,
        'text': 'Workers can easily be deployed on any machines or services using the following docker compose file:<pre>version: "3.4"\nservices:\n  worker:\n    image: patcas/prvobs:worker\n    # restart: always\n    privileged: true\n    environment:\n      # always use prefix of http:// or https:// for declaring the host\n      api_host: http://X.X.X.X:5000\n      api_tkn: XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX\n    network_mode: "host"\n    volumes:\n      # needs to be mapped as reference files for the worker to pass and extract inputs / ouputs to studies\n      - /opt/input.txt:/opt/input.txt\n      - /opt/output.txt:/opt/output.txt\n      # docker socket needs to be mapped inside of the worker container\n      - /var/run/docker.sock:/var/run/docker.sock</pre>',
        'fields': {
            'name': {},
        }
    },
    'users': {
        'adding': true,
        'editing': true,
        'text': 'Users have automatically access on the website as well as on the RestAPI endpoint and can thus also execute all API calls directly. The access on the website is granted by using a JWT token after the initial login.',
        'fields': {
            'name': {},
            'email': {},
            'password': {},
        }
    },
    'runs': {
        'adding': true,
        'editing': false,
        'text': 'Runs are automatically generated by the periodic execution of studies. The associated measurements can be viewed by clicking on the details of a specific run.<br><br>In order to register the original measurements from a paper, you can add these by clicking Add Measurements, select a study and insert a timestamp and stats in the following format:<br><br>Timestamp:<pre>Wed, 05 May 2021 12:00:00 GMT</pre>Stats:<pre>{\n  "key1": value,\n  "key2": value\n}</pre>',
        'fields': {
            'study_id': {},
            'timestamp': {},
            'stats': {
                'multiline': true,
                'parse_before_send': true,
            },
            'output': {
                'multiline': true,
            },
        }
    }
}

// cache for json obj
view_prototype.open_edit_data = null;

view_prototype.load_view = (callback) => {
    document.getElementById('dynamic_content').innerHTML = '';
    addLoadingSpinner(document.getElementById('dynamic_content'));
    api_prototype.api_call('GET', '/' + nav_prototype.curr_page, null, (route, json) => {
        view_prototype.display_view(callback, route, json);
    });
};

view_prototype.display_view = (callback, route, json) => {
    // Handle Title
    if(nav_prototype.curr_page_elem != null) {
        nav_prototype.curr_page_title = nav_prototype.curr_page_singular.ucwords() + ' ' + json['id'];
        if (Object.keys(json).includes('name')) {
            nav_prototype.curr_page_title = json['name'];
        }
    }
    else {
        nav_prototype.curr_page_title = document.getElementById('menu_' + nav_prototype.curr_page_group).textContent.trim();
    }

    // Handle Breadcrump
    let grandParentElem = document.getElementById('menu_' + nav_prototype.curr_page_group).parentElement.parentElement.parentElement;
    let breadcrumb_sublabel = '';
    if(nav_prototype.curr_page_elem != null) {
        breadcrumb_sublabel = grandParentElem.firstElementChild.textContent.trim() + ' / ' + document.getElementById('menu_' + nav_prototype.curr_page_group).textContent.trim();
    }
    else if(grandParentElem.classList.contains('menu-item')) {
        breadcrumb_sublabel = grandParentElem.firstElementChild.textContent.trim();
    }
    else {
        breadcrumb_label = document.getElementById('menu_' + nav_prototype.curr_page_group).textContent.trim();
    }

    document.getElementById('breadcrumbs').innerHTML = ((breadcrumb_sublabel != '') ? '<span class="text-muted fw-light">' + breadcrumb_sublabel + ' /</span> ' : '') + nav_prototype.curr_page_title;

    // Generate Body
    document.getElementById('dynamic_content').innerHTML = '';

    // Generate Table Part of the Body
    let table_route = null;
    let table_title = null;
    let table_data = null;

    // If json is an array, we are at the group page
    if (Array.isArray(json)) {
        table_route = nav_prototype.curr_page;
        table_title = nav_prototype.curr_page_title;
        table_data = json;

        // Generate Header Card
        document.getElementById('dynamic_content').innerHTML += '<div class="card mb-4"> \
                                <h5 class="card-header">Informations</h5> \
                                <div class="card-body"> \
                                    <p class="card-text"> \
                                    ' + view_prototype.static_settings[nav_prototype.curr_page].text + ' \
                                    </p> \
                                </div> \
                            </div>';
    }
    // otherwise, we have selected a specific element
    else {
        let content_html = '';

        // check if json contains num fields for widgets
        for(let idx_scan in json) {
            if(idx_scan.includes('num_')) {
                content_html += '<div class="row">';
                for(let idx in json) {
                    if(idx.includes('num_')) {
                        content_html += '<div class="col-lg-3 col-md-12 col-6 mb-4"> \
                                            <div class="card"> \
                                                <div class="card-body"> \
                                                <span class="fw-semibold d-block mb-1">' + idx.replaceAll('num_', '').beautify() + '</span> \
                                                <h3 class="card-title mb-2 ' + ((json[idx] != '0') ? 'text-success' : 'text-danger') + '">' + json[idx] + '</h3> \
                                                </div> \
                                            </div> \
                                        </div>';
                    }
                }

                content_html += '</div>';

                break;
            }
        }

        // check if json contains non-num fields for card text
        let card_data = {};
        for(let idx in json) {
            if(idx.includes('num_')) {
                continue;
            }

            if(typeof json[idx] == 'number' || typeof json[idx] == 'boolean') {
                json[idx] = json[idx].toString();
            }

            if(typeof json[idx] == 'string') {
                // check if the string is hex, if yes, decode it
                let value = json[idx];
                if(value.substring(0, 2) == '\\x') {
                    value = hex2a(value.substring(2));
                }

                if(value.includes('\\n')) {
                    value = value.replaceAll('\\n', '\n');
                }

                card_data[idx.beautify()] = value;
            }
        }

        if(Object.keys(card_data).length != 0) {
            // Generate Header Card
            content_html += '<div class="card mb-4"> \
                                    <h5 class="card-header">' + nav_prototype.curr_page_title + '</h5> \
                                    <div class="card-body">';
            
                for(let idx in card_data) {
                    content_html += '<div class="row mb-3"> \
                                        <label class="col-sm-2 col-form-label" for="basic-default-name">' + idx + '</label> \
                                        <div class="col-sm-10" style="padding-top: calc(0.4375rem + 1px);"><pre>' + card_data[idx] + '</pre></div> \
                                    </div>';
                }

            content_html += '</div> \
                        </div>';
        }
        
        document.getElementById('dynamic_content').innerHTML += content_html;

        // Make Timeline
        for(let idx in json) {
            if(isDict(json[idx])) {
                document.getElementById('dynamic_content').innerHTML += view_prototype.display_view_timeline(idx, json[idx]);
                break;
            }
        }

        // Make Table
        for(let idx in json) {
            if(Array.isArray(json[idx])) {
                table_route = idx;
                table_title = idx.ucwords();
                table_data = json[idx];
                
                break;
            }
        }
    }

    if(table_data != null) {
        document.getElementById('dynamic_content').innerHTML += view_prototype.display_view_table(table_route, table_title, table_data);
    }

    // In case a callback function was passed, execute it, since page loading is fininshed
    if(callback) {
        callback();
    }
};

view_prototype.display_view_timeline = (timescale_title, timescale_data) => {
    console.log(['this is a pb', timescale_data]);
    dyn_content_html = '<div class="card mb-4"> \
                            <h5 class="card-header">' + timescale_title.ucwords() + '</h5> \
                            <div class="card-body"> \
                                <div id="timeChartHolder"></div> \
                            </div> \
                        </div>';

    let data = [];
    for (let label in timescale_data) {
        let x_data = [];
        let y_data = [];
        let error_y = null;

        for (let date in timescale_data[label]) {
            console.log([timescale_data[label][date], typeof timescale_data[label][date]]);
            let y_val = null;
            if (typeof timescale_data[label][date] == 'string') {
                if (timescale_data[label][date] == 'true') {
                    y_val = 1;
                }
                else if (timescale_data[label][date] == 'false') {
                    y_val = 0;
                }
            }
            else if (typeof timescale_data[label][date] == 'object') {
                y_val = timescale_data[label][date].mean;

                if(error_y == null) {
                    error_y = {
                        type: 'data',
                        array: [],
                        visible: true
                    };
                }

                error_y.array.push(timescale_data[label][date].std);
            }
            else {
                y_val = timescale_data[label][date];
            }
    
            x_data.push(date);
            y_data.push(y_val);
        }
    
        data.push({
            x: x_data,
            y: y_data,
            type: 'scatter',
            error_y: error_y,
            name: label,
            mode: 'lines+markers',
        });
    }

    setTimeout(function() {
        Plotly.newPlot('timeChartHolder', data, {
            xaxis: {
                title: 'Time',
                zeroline: true,
                showline: true,
            },
            yaxis: {
                showline: true,
                rangemode: 'tozero',
            }
        });
    }, 100);

    return dyn_content_html;
}

view_prototype.display_view_table = (table_route, table_title, table_data) => {
    // Remove focus from the currently active element
    document.activeElement.blur();

    dyn_content_html = '';
    dyn_content_html += '<!-- Basic Bootstrap Table --> \
    <div class="card"> \
    <h5 class="card-header">' + table_title + '</h5> \
    <div class="table-responsive text-nowrap"> \
        <table class="table table-striped table-hover">';
        if(nav_prototype.curr_page_elem == null && view_prototype.static_settings[table_route].adding) {
            dyn_content_html += '<caption class="ms-4"> \
                <div class="demo-inline-spacing"> \
                    <button type="button" style="margin-bottom: 75px !important;" class="btn btn-primary" onclick="view_prototype.display_new(\'' + table_route + '\')" data-bs-toggle="modal" data-bs-target="#largeModal">Add ' + table_route.slice(0, -1).ucwords() + '</button> \
                </div> \
            </caption>';
        }
        dyn_content_html += '<thead> \
            <tr><th>ID</th>';
            if(table_data.length == 0) {
                dyn_content_html += '<th>Name</th><th>Timestamp</th>';
            }
            else {
                for (let idx in table_data[0]) {
                    if (
                        (
                            !Object.keys(view_prototype.static_settings).includes(table_route)
                            || !Object.keys(view_prototype.static_settings[table_route]['fields']).includes(idx)
                            || !view_prototype.static_settings[table_route]['fields'][idx]['multiline']
                        )
                        && !(idx.includes('num_') || idx.includes('_date') || idx == 'id' || idx == 'token')
                    ) {
                        dyn_content_html += '<th>' + idx.beautify() + '</th>';
                    }
                }
            }

            if(Object.keys(view_prototype.static_settings).includes(table_route)) {
                dyn_content_html += '<th>Actions</th>';
            }

    dyn_content_html += '</tr> \
        </thead> \
        <tbody class="table-border-bottom-0">';

        for (let i in table_data) {
            dyn_content_html += '<tr><td>' + table_data[i]['id'] + '</td>';

            for(let idx in table_data[i]) {
                if (
                    (
                        !Object.keys(view_prototype.static_settings).includes(table_route)
                        || !Object.keys(view_prototype.static_settings[table_route]['fields']).includes(idx)
                        || !view_prototype.static_settings[table_route]['fields'][idx]['multiline']
                    )
                    && !(idx.includes('num_') || idx.includes('_date') || idx == 'id' || idx == 'token')
                ) {
                    // Make check icons for booleans
                    if(idx.includes('is_')) {
                        if (table_data[i][idx]) {
                            table_data[i][idx] = '<i class="bx bx-check text-success fw-semibold"></i>';
                        }
                        else {
                            table_data[i][idx] = '<i class="bx bx-x text-danger fw-semibold"></i>';
                        }
                    }
                    dyn_content_html += '<td>' + table_data[i][idx] + '</td>';
                }
            }

            if(Object.keys(view_prototype.static_settings).includes(table_route)) {
                dyn_content_html += '<td> \
                                        <div class="dropdown"> \
                                            <button type="button" class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown"> \
                                            <i class="bx bx-dots-vertical-rounded"></i> \
                                            </button> \
                                            <div class="dropdown-menu">';


                    if(nav_prototype.curr_page_elem == null
                        && view_prototype.static_settings[table_route].editing){
                        dyn_content_html += '<a class="dropdown-item" href="javascript:void(0);" onclick="view_prototype.load_edit(this)" data-bs-toggle="modal" data-bs-target="#largeModal" data-row_id="' + table_data[i]['id'] + '" \
                                                ><i class="bx bx-edit-alt me-2"></i> Edit</a> \
                                            <a class="dropdown-item" href="javascript:void(0);" onclick="view_prototype.delete_entity(this)" data-row_id="' + table_data[i]['id'] + '"\
                                                ><i class="bx bx-trash me-2"></i> Delete</a>';
                    }

                    dyn_content_html += '<a class="dropdown-item" href="javascript:void(0);" onclick="nav_prototype.open_page(\'' + table_route + '/' + table_data[i]['id'] + '\')" \
                        ><i class="bx bx-bar-chart me-2"></i> Details</a>';
                        
                    dyn_content_html += '</div> \
                                        </div> \
                                    </td>';
            }

            dyn_content_html += '</tr>';
        }

    dyn_content_html += '</tbody> \
        </table> \
    </div> \
    </div> \
    <!--/ Basic Bootstrap Table -->';

    return dyn_content_html;
};

view_prototype.load_edit = (elem = null) => {
    if(elem != null) {
        nav_prototype.curr_page_elem = elem.dataset.row_id;
    }

    document.getElementById('modal_title').innerHTML = 'Edit ' + nav_prototype.curr_page_singular.ucwords();
    document.getElementById('modal_body').innerHTML = '';
    addLoadingSpinner(document.getElementById('modal_body'));
    api_prototype.api_call('GET', '/' + nav_prototype.curr_page + '/' + nav_prototype.curr_page_elem, null, view_prototype.display_edit);
};

view_prototype.display_new = (obj_route) => {
    console.log(["Open Edit Window", obj_route])
    document.getElementById('modal_title').innerHTML = 'New ' + obj_route.slice(0, -1).ucwords();
    document.getElementById('modal_body').innerHTML = '';

    for(let idx in view_prototype.static_settings[obj_route]['fields']) {
        document.getElementById('modal_body').innerHTML += '<div class="row mb-3"> \
                <label class="col-sm-2 col-form-label" for="basic-default-name">' + idx.beautify() + '</label> \
                <div class="col-sm-10">' + view_prototype.generate_field(obj_route, idx, '') + '</div> \
            </div>';
    }
};

view_prototype.display_edit = (route, json) => {
    view_prototype.open_edit_data = json;
    for (let idx in json) {
        if(json[idx] != null && typeof json[idx] == 'object') {
            continue;
        }

        document.getElementById('modal_body').innerHTML += '<div class="row mb-3"> \
                <label class="col-sm-2 col-form-label" for="basic-default-name">' + idx.beautify() + '</label> \
                <div class="col-sm-10">' + view_prototype.generate_field(nav_prototype.curr_page_group, idx, json[idx]) + '</div> \
            </div>';
    }

    // for hidden input fields (like password) generate these client side
    for (let idx in view_prototype.static_settings[nav_prototype.curr_page]['fields']) {
        if (!Object.keys(json).includes(idx)) {
            document.getElementById('modal_body').innerHTML += '<div class="row mb-3"> \
                <label class="col-sm-2 col-form-label" for="basic-default-name">' + idx.beautify() + '</label> \
                <div class="col-sm-10">' + view_prototype.generate_field(nav_prototype.curr_page_group, idx, '') + '</div> \
            </div>';
        }
    }
};

view_prototype.generate_field = (obj_route, name, value) => {
    if(name.substr(-3) == '_id') {
        let routes = name.split('_')[0] + 's';

        api_prototype.api_call('GET', '/' + routes, null, view_prototype.display_edit_selections);
        return '<select id="defaultSelect" class="form-select" name="' + name + '"></select>';
    }
    else if (name.includes('is_') || name.includes('num_') || name.includes('_date') || (name.includes('timestamp') && value != '') || name == 'id' || name == 'token') {
        return '<input type="text" class="form-control" name="' + name + '" value="' + value + '" readonly required="true">';
    }
    else if (Object.keys(view_prototype.static_settings[obj_route]['fields']).includes(name)
        && view_prototype.static_settings[obj_route]['fields'][name]['multiline']) {
        return '<textarea class="form-control" name="' + name + '" rows="8" required="true">' + value + '</textarea>';
    }
    else {
        let attr_ext = '';
        if (name.includes('cron')) {
            /*attr_ext += ' pattern="^(?#minute)(\*|(?:[0-9]|(?:[1-5][0-9]))(?:(?:\-[0-9]|\-(?:[1-5][0-9]))?|\
            (?:\,(?:[0-9]|(?:[1-5][0-9])))*)) (?#hour)(\*|(?:[0-9]|1[0-9]|2[0-3])\
            (?:(?:\-(?:[0-9]|1[0-9]|2[0-3]))?|(?:\,(?:[0-9]|1[0-9]|2[0-3]))*))\
            (?#day_of_month)(\*|(?:[1-9]|(?:[12][0-9])|3[01])(?:(?:\-(?:[1-9]|\
            (?:[12][0-9])|3[01]))?|(?:\,(?:[1-9]|(?:[12][0-9])|3[01]))*)) (?#month)(\*|\
            (?:[1-9]|1[012]|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(?:(?:\-(?:[1-9]|\
            1[012]|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))?|(?:\,(?:[1-9]|1[012]|\
            JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))*)) (?#day_of_week)(\*|\
            (?:[0-6]|SUN|MON|TUE|WED|THU|FRI|SAT)(?:(?:\-(?:[0-6]|SUN|MON|TUE|WED|THU|FRI|SAT))?|\
            (?:\,(?:[0-6]|SUN|MON|TUE|WED|THU|FRI|SAT))*))$"';*/
        }

        return '<input type="text" class="form-control" name="' + name + '" value="' + value + '" ' + attr_ext +' required="true">';
    }
}

view_prototype.display_edit_selections = (route, json) => {
    const field_name = route.slice(1, -1) + '_id';

    document.getElementsByName(field_name)[0].innerHTML += '<option ' + (view_prototype.open_edit_data && view_prototype.open_edit_data[field_name] == null ? 'selected' : '') + '>None</option>';

    for (let i in json) {
        document.getElementsByName(field_name)[0].innerHTML += '<option value="' + json[i].id + '" ' + (view_prototype.open_edit_data && view_prototype.open_edit_data[field_name] == json[i].id ? 'selected' : '') + '>' + json[i].name + '</option>';
    }
}

view_prototype.save_modal = () => {
    let post_req = {};

    const form = document.getElementById('largeModal');
    if(!form.reportValidity()) {
        return
    }

    for (let idx in form.elements) {
        if(document.getElementsByName(idx).length != 0) {
            input_field = document.getElementsByName(idx)[0];

            if (Object.keys(view_prototype.static_settings).includes(nav_prototype.curr_page) &&
                Object.keys(view_prototype.static_settings[nav_prototype.curr_page].fields).includes(input_field.name) &&
                Object.keys(view_prototype.static_settings[nav_prototype.curr_page].fields[input_field.name]).includes('parse_before_send') &&
                view_prototype.static_settings[nav_prototype.curr_page].fields[input_field.name].parse_before_send) {
                post_req[input_field.name] = input_field = JSON.parse(input_field.value);
            }
            else {
                post_req[input_field.name] = input_field.value;
            }
        }
    }

    const post_req_str = JSON.stringify(post_req);

    if(nav_prototype.curr_page_elem != null) {
        api_prototype.api_call('PUT', '/' + nav_prototype.curr_page + '/' + nav_prototype.curr_page_elem, post_req_str, view_prototype.close_modal);
    }
    else {
        api_prototype.api_call('POST', '/' + nav_prototype.curr_page, post_req_str, view_prototype.close_modal);
    }
};

view_prototype.close_modal = () => {
    $('#largeModal').modal('hide');

    // reset Element
    nav_prototype.curr_page_elem = null;

    // reload the active page
    view_prototype.load_view();
};

view_prototype.delete_entity = (elem) => {
    let check_value = prompt("To confirm the deletion, input the following id: " + elem.dataset.row_id, "");
    if(check_value != elem.dataset.row_id) {
        addErrorNotification('Input was not correct (' + elem.dataset.row_id + ' != ' + check_value + ')!');
        return;
    }

    api_prototype.api_call('DELETE', '/' + nav_prototype.curr_page + '/' + elem.dataset.row_id, null, view_prototype.finalize_deletion);
};

view_prototype.finalize_deletion = () => {
    view_prototype.load_view();
};

document.getElementById("modal_save_btn").addEventListener("click", view_prototype.save_modal, false);