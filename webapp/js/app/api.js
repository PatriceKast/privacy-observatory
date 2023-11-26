function api_prototype() { }

api_prototype.api_host = 'http://localhost/api';
api_prototype.api_call = async (method, route, payload, callback_succ, callback_fail = null, http_auth = null) => {
    let headers = new Headers();
    headers.set('Content-Type', 'application/json');

    if (http_auth) {
        headers.set('Authorization', 'Basic ' + btoa(http_auth[0] + ":" + http_auth[1]));
    }
    else {
        headers.set('Authorization', 'Basic ' + btoa(app_state['user']['token'] + ":" + 'notUsed'));
    }

    // in case the route ends with a slash, remove it
    if(route.slice(-1) == '/') {
        route = route.slice(0, -1);
    }

    try {
        const response = await fetch(api_prototype.api_host + route, {
            method: method,
            body: payload, // string or object
            headers: headers
        });

        console.log(["response", response]);

        // Remove loading spinners
        Array.from(document.getElementsByClassName('loading_spinner')).forEach(function (element) {
            element.remove();
        });

        // If we get an non authorized error, sign out the user
        if (response.status == 401) {
            login_prototype.logout();
        }
        
        if (!response.ok) {
            let error_msg = "Network response was not OK";
            try {
                const errorText = await response.text();
                error_msg = JSON.parse(errorText).error;
            } catch (error) {}

            throw new Error(error_msg);
        }

        const respText = await response.text(); //extract JSON from the http response

        let myJson = {};
        if(respText != '') {
            myJson = JSON.parse(respText);
        }

        callback_succ(route, myJson);
    } catch (error) {
        console.log(["got error: ", error]);
        if(app_state['logged_in']) {
            addErrorNotification(error);
        }

        if(callback_fail != null) {
            callback_fail();
        }
    }
}