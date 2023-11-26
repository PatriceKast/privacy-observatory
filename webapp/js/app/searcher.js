function searcher_prototype() { }

searcher_prototype.make_search = () => {
    let search_str = document.getElementById('search_input').value;

    api_prototype.api_call ('GET', '/domains?filter=' + search_str, null, searcher_prototype.display_search); 
};

searcher_prototype.display_search = (route, json) => {
    console.log(json);

    document.getElementById('search_results').innerHTML = '';
    if (json.length == 0) {
        document.getElementById('search_results').innerHTML += '<a href="javascript:void(0);" class="search-result disabled">No results found!</a>';
    }
    else {
        let count_loops = 0;
        for(idx in json) {
            count_loops ++;
            if (count_loops > 10){
                break;
            }
            
            document.getElementById('search_results').innerHTML += '<a href="javascript:void(0);" class="search-result ' + ((nav_prototype.curr_page_group == 'domains' && nav_prototype.curr_page_elem == json[idx]['id']) ? 'active' : '') + '" onclick="nav_prototype.open_page(\'domains/' + json[idx]['id'] + '\', searcher_prototype.make_search)">' + json[idx]['name'] + '</a>';
        }
    
    }
}