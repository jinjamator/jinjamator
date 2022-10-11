var dropdown_states = {}
var debug_frontend = true;
var result_cache = {}


log.setLevel(logging.FE_DEBUG)

function table_dropdown_set_value(select, container) {
    window.setTimeout( // this is needed for alpaca to have data in the parent row
        function () {

            let dropdown = Alpaca.fieldInstances[select[0].id]
            let options = dropdown.options.jinjamator.table_dropdown_set_value
            $(container[0]).children("button")[0].disabled = true
            $(container[0]).children("button")[0].title = 'Loading...'
            $(container[0]).children("button").children("span")[0].innerText = 'Loading...'

            var site = $('#jinjamator_environment option:selected').val()
            let url = options.url
            let mappings = options.mappings
            let post_data = options.post_data

            let task_configuration = process_mappings(post_data, dropdown.parent.getValue(), dropdown)
            log.debug(select[0].id, "task_configuration after mapping", task_configuration)
            client.tasks.read(url,
                {
                    'preload-data': JSON.stringify(task_configuration),
                    'preload-defaults-from-site': site
                }).done(function (preload_result) {
                    task_configuration = preload_result['data']
                    log.debug(select[0].id, 'got task configuration', task_configuration)
                    task_configuration['output_plugin'] = "json";
                    client.tasks.create(url, task_configuration).done(function (task_result) {
                        log.debug(select[0].id, 'got task result', task_result)

                        task_result = process_mappings(mappings, task_result);
                        log.debug(select[0].id, "setting dropdown value to" + task_result[dropdown.propertyId], task_result, dropdown)
                        dropdown.setValue(task_result[dropdown.propertyId])

                        // dropdown.refresh() this loops with multiselect onInizialized -> just select via multiselect
                        $('#' + dropdown.id).multiselect('select', task_result[dropdown.propertyId]);

                        //unlock dropdown
                        $(container[0]).children("button")[0].disabled = false

                        // call onDone callback if configured
                        if (options.onDone) {
                            if (options.onDone in window) {
                                window[options.onDone](select, container)
                            }
                            else {
                                log.error("Cannot find onDone function" + options.onDone)
                            }
                        }


                    }).fail(function (e) {
                        log.error(select[0].id, "failed to create task", "url:", url, "task_configuration", task_configuration, 'site', site)
                        $("#overlay").fadeOut(1);
                        throw (e)
                    })

                }).fail(function (e) {
                    log.error(select[0].id, "cannot preload task data ", "url:", url, "task_configuration", task_configuration, 'site', site)
                    $("#overlay").fadeOut(1);
                    throw (e)
                })

        }
        , 1)


}

function process_mappings(mappings, data, obj = {}) {

    for (const [key, code] of Object.entries(mappings)) {
        if (code in window) {
            data[key] = window[code](key, data, obj)
        }
        else {
            try {
                data[key] = jq.json(data, code)
            } catch (e) {
                log.error(e)
            }
        }

    }
    log.debug("process_mappings return value", data)
    return data

}

function dropdown_fill_dropdown(element, checked) {
    let dropdown_id = element[0].parentNode.id
    let options = Alpaca.fieldInstances[dropdown_id].options.jinjamator.dropdown_fill_dropdown
    dropdown_fill_callback(element, checked, options, function (url, target, task_result) {
        log.setPrefix("dropdown_fill_dropdown/dropdown_fill_callback/callback")
        for (const [key, value] of Object.entries(task_result)) {
            target.schema.enum.push(key);
            target.options.optionLabels.push(value["label"]);
            if (!(element in result_cache[url]['byElement']))
                result_cache[url]['byElement'][element] = {};
            result_cache[url][key] = task_result[key]["data"]
            result_cache[url]['byElement'][element][key] = task_result[key]["data"]
        };
    })
}

function dropdown_fill_table(element, checked) {
    let dropdown_id = element[0].parentNode.id
    let options = Alpaca.fieldInstances[dropdown_id].options.jinjamator.dropdown_fill_table
    dropdown_fill_callback(element, checked, options, function (url, target, task_result) {
        log.setPrefix("dropdown_fill_table/dropdown_fill_callback/callback")
        let dropdown_id = element[0].parentNode.id
        let dropdown = Alpaca.fieldInstances[dropdown_id]
        let element_value = element[0].value


        let row_data = {}
        if (options.mappings !== undefined) {
            $("#overlay").fadeIn(100); // this is needed because emscripten jq is noticeably slow
            task_result[element_value] = process_mappings(options.mappings, task_result[element_value]);
            window.setTimeout(
                function () { $("#overlay").fadeOut(1); }
                , 150)

        }


        for (const [key, value] of Object.entries(target.options.items.fields)) {
            try {
                row_data[key] = task_result[element_value][key]
            } catch (e) {
                log.error(e)
                row_data[key] = ""
            }

        }
        var value = target.getValue();

        if (target.__key_cache__ === undefined) {
            target.__key_cache__ = []
        }

        if (checked) {
            target.__key_cache__.push(element_value)
            var idx = target.__key_cache__.indexOf(element_value)
            value.push(row_data);
        }
        else {
            var idx = target.__key_cache__.indexOf(element_value)
            value.splice(idx, 1)
            target.__key_cache__.splice(idx, 1)
        }
        target.setValue(value);
        $("td.dataTables_empty").parent().remove() // workaround alpaca datatables bug

    })
}


function dropdown_fill_callback(element, checked, options, callback) {
    // helper function to update a target alpaca item based on the results of a backend jinjamator task
    if (options.collapse_on_select){
        $(document).click(); // collapse dropdown
    }
    

    let element_index = element[0].index
    let dropdown_id = element[0].parentNode.id
    let dropdown = Alpaca.fieldInstances[dropdown_id]
    let value = element[0].value
    let site = $('#jinjamator_environment option:selected').val()
    let task_configuration = {}


    try {
        var target_name = options.target
    } catch (e) {
        log.error("mandatory config.", dropdown.name, ".options.jinjamator.target is missing")
        throw (e)
    }
    try {
        var url = options.url
    } catch (e) {
        log.error("", dropdown.name, ".options.jinjamator.url undefined")
        throw (e)
    }

    try {
        var target = $("#form").alpaca("get").getControlByPath(target_name);
    }
    catch (e) {
        log.error("cannot find alpaca target field.", target_name)
        throw (e)
    }
    
    log.debug(dropdown.path, " index: ", element_index, " ", element, " is checked", checked, " value is: ", value)

    // convert get parameter to post
    if (url.includes("?")) {
        [url, params] = url.replace('{value}', value).split("?")
        for (const param of new URLSearchParams("?" + params).entries()) {
            task_configuration[param[0]] = param[1]
        }
        log.debug("URL", url)
    }

    if (url.startsWith("cache:")) {
        cache_key = url.substring(6)
        log.debug("cache URL", cache_key)
        task_result = result_cache[cache_key]
        callback(url, target, task_result);
        return 0
    }


    if (!(url in result_cache)) {
        result_cache[url] = {};
        result_cache[url]['byElement'] = {};
    }


    if (checked == true) {

        $("#overlay").fadeIn(100);
        client.tasks.read(url,
            {
                'preload-data': JSON.stringify(task_configuration),
                'preload-defaults-from-site': site
            }).done(function (preload_result) {
                task_configuration = preload_result['data']
                log.debug('got task configuration', task_configuration)
                task_configuration['output_plugin'] = "json";
                client.tasks.create(url, task_configuration).done(function (task_result) {
                    log.debug('got task result', task_result)
                    callback(url, target, task_result);
                    target.refresh(function () {
                        $("#overlay").fadeOut(1);
                    });

                }).fail(function (e) {
                    log.error("failed to create task", "url:", url, "task_configuration", task_configuration, 'site', site)
                    $("#overlay").fadeOut(1);
                    throw (e)
                })

            }).fail(function (e) {
                log.error("cannot preload task data ", "url:", url, "task_configuration", task_configuration, 'site', site)
                $("#overlay").fadeOut(1);
                throw (e)
            })

    } else {
        log.debug("deselecting values", result_cache[url]['byElement'][element])
        // $("#overlay").fadeIn(100);
        for (const [key, value] of Object.entries(result_cache[url]['byElement'][element])) {
            const index = target.schema.enum.indexOf(key);

            if (index > -1) {
                target.schema.enum.splice(index, 1);
                target.options.optionLabels.splice(index, 1);
                for (const [d_i, d_v] of Object.entries(target.data)) {
                    if (key == d_v.text) {
                        target.data.splice(d_i, 1);
                    }
                }

            }

        };
        target.refresh(function () {
            log.debug("finished deselecting")
        });
    }
}