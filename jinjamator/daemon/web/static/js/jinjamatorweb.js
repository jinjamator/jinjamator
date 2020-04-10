/**
 * AdminLTE Demo Menu
 * ------------------
 * You should not use this file in production.
 * This file is for demo purposes only.
 */
$(function() {
    'use strict'

    /**
     * Get access to plugins
     */

    $('[data-toggle="control-sidebar"]').controlSidebar()
    $('[data-toggle="push-menu"]').pushMenu()
    var $pushMenu = $('[data-toggle="push-menu"]').data('lte.pushmenu')
    var $controlSidebar = $('[data-toggle="control-sidebar"]').data('lte.controlsidebar')
    var $layout = $('body').data('lte.layout')
    $(window).on('load', function() {
        // Reinitialize variables on load
        $pushMenu = $('[data-toggle="push-menu"]').data('lte.pushmenu')
        $controlSidebar = $('[data-toggle="control-sidebar"]').data('lte.controlsidebar')
        $layout = $('body').data('lte.layout')
    })

    /**
     * List of all the available skins
     *
     * @type Array
     */
    var mySkins = [
        'skin-blue',
        'skin-black',
        'skin-red',
        'skin-yellow',
        'skin-purple',
        'skin-green',
        'skin-blue-light',
        'skin-black-light',
        'skin-red-light',
        'skin-yellow-light',
        'skin-purple-light',
        'skin-green-light'
    ]

    /**
     * Get a prestored setting
     *
     * @param String name Name of of the setting
     * @returns String The value of the setting | null
     */
    function get(name) {
        if (typeof(Storage) !== 'undefined') {
            return localStorage.getItem(name)
        } else {
            window.alert('Please use a modern browser to properly view this template!')
        }
    }

    /**
     * Store a new settings in the browser
     *
     * @param String name Name of the setting
     * @param String val Value of the setting
     * @returns void
     */
    function store(name, val) {
        if (typeof(Storage) !== 'undefined') {
            localStorage.setItem(name, val)
        } else {
            window.alert('Please use a modern browser to properly view this template!')
        }
    }

    /**
     * Toggles layout classes
     *
     * @param String cls the layout class to toggle
     * @returns void
     */
    function changeLayout(cls) {
        $('body').toggleClass(cls)
        $layout.fixSidebar()
        if ($('body').hasClass('fixed') && cls == 'fixed') {
            $pushMenu.expandOnHover()
            $layout.activate()
        }
        $controlSidebar.fix()
    }

    /**
     * Replaces the old skin with the new skin
     * @param String cls the new skin class
     * @returns Boolean false to prevent link's default action
     */
    function changeSkin(cls) {
        $.each(mySkins, function(i) {
            $('body').removeClass(mySkins[i])
        })

        $('body').addClass(cls)
        store('skin', cls)
        return false
    }

    /**
     * Retrieve default settings and apply them to the template
     *
     * @returns void
     */
    function setup() {
        var tmp = get('skin')
        if (tmp && $.inArray(tmp, mySkins))
            changeSkin(tmp)

        // Add the change skin listener
        $('[data-skin]').on('click', function(e) {
            if ($(this).hasClass('knob'))
                return
            e.preventDefault()
            changeSkin($(this).data('skin'))
        })

        // Add the layout manager
        $('[data-layout]').on('click', function() {
            changeLayout($(this).data('layout'))
        })

        $('[data-controlsidebar]').on('click', function() {
            changeLayout($(this).data('controlsidebar'))
            var slide = !$controlSidebar.options.slide

            $controlSidebar.options.slide = slide
            if (!slide)
                $('.control-sidebar').removeClass('control-sidebar-open')
        })

        $('[data-sidebarskin="toggle"]').on('click', function() {
            var $sidebar = $('.control-sidebar')
            if ($sidebar.hasClass('control-sidebar-dark')) {
                $sidebar.removeClass('control-sidebar-dark')
                $sidebar.addClass('control-sidebar-light')
            } else {
                $sidebar.removeClass('control-sidebar-light')
                $sidebar.addClass('control-sidebar-dark')
            }
        })

        $('[data-enable="expandOnHover"]').on('click', function() {
            $(this).attr('disabled', true)
            $pushMenu.expandOnHover()
            if (!$('body').hasClass('sidebar-collapse'))
                $('[data-layout="sidebar-collapse"]').click()
        })

        //  Reset options
        if ($('body').hasClass('fixed')) {
            $('[data-layout="fixed"]').attr('checked', 'checked')
        }
        if ($('body').hasClass('layout-boxed')) {
            $('[data-layout="layout-boxed"]').attr('checked', 'checked')
        }
        if ($('body').hasClass('sidebar-collapse')) {
            $('[data-layout="sidebar-collapse"]').attr('checked', 'checked')
        }

    }

    // Create the new tab
    var $tabPane = $('<div />', {
        'id': 'control-sidebar-theme-demo-options-tab',
        'class': 'tab-pane active'
    })

    // Create the tab button
    var $tabButton = $('<li />', { 'class': 'active' })
        .html('<a href=\'#control-sidebar-theme-demo-options-tab\' data-toggle=\'tab\'>' +
            '<i class="fa fa-wrench"></i>' +
            '</a>')

    // Add the tab button to the right sidebar tabs
    $('[href="#control-sidebar-home-tab"]')
        .parent()
        .before($tabButton)

    // Create the menu
    var $demoSettings = $('<div />')

    // Layout options
    $demoSettings.append(
        '<h4 class="control-sidebar-heading">' +
        'Layout Options' +
        '</h4>'
        // Fixed layout
        +
        '<div class="form-group">' +
        '<label class="control-sidebar-subheading">' +
        '<input type="checkbox"data-layout="fixed"class="pull-right"/> ' +
        'Fixed layout' +
        '</label>' +
        '<p>Activate the fixed layout. You can\'t use fixed and boxed layouts together</p>' +
        '</div>'
        // Boxed layout
        +
        '<div class="form-group">' +
        '<label class="control-sidebar-subheading">' +
        '<input type="checkbox"data-layout="layout-boxed" class="pull-right"/> ' +
        'Boxed Layout' +
        '</label>' +
        '<p>Activate the boxed layout</p>' +
        '</div>'
        // Sidebar Toggle
        +
        '<div class="form-group">' +
        '<label class="control-sidebar-subheading">' +
        '<input type="checkbox"data-layout="sidebar-collapse"class="pull-right"/> ' +
        'Toggle Sidebar' +
        '</label>' +
        '<p>Toggle the left sidebar\'s state (open or collapse)</p>' +
        '</div>'
        // Sidebar mini expand on hover toggle
        +
        '<div class="form-group">' +
        '<label class="control-sidebar-subheading">' +
        '<input type="checkbox"data-enable="expandOnHover"class="pull-right"/> ' +
        'Sidebar Expand on Hover' +
        '</label>' +
        '<p>Let the sidebar mini expand on hover</p>' +
        '</div>'
        // Control Sidebar Toggle
        +
        '<div class="form-group">' +
        '<label class="control-sidebar-subheading">' +
        '<input type="checkbox"data-controlsidebar="control-sidebar-open"class="pull-right"/> ' +
        'Toggle Right Sidebar Slide' +
        '</label>' +
        '<p>Toggle between slide over content and push content effects</p>' +
        '</div>'
        // Control Sidebar Skin Toggle
        +
        '<div class="form-group">' +
        '<label class="control-sidebar-subheading">' +
        '<input type="checkbox"data-sidebarskin="toggle"class="pull-right"/> ' +
        'Toggle Right Sidebar Skin' +
        '</label>' +
        '<p>Toggle between dark and light skins for the right sidebar</p>' +
        '</div>'
    )
    var $skinsList = $('<ul />', { 'class': 'list-unstyled clearfix' })

    // Dark sidebar skins
    var $skinBlue =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-blue" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div><span style="display:block; width: 20%; float: left; height: 7px; background: #367fa9"></span><span class="bg-light-blue" style="display:block; width: 80%; float: left; height: 7px;"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #222d32"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin">Blue</p>')
    $skinsList.append($skinBlue)
    var $skinBlack =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-black" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div style="box-shadow: 0 0 2px rgba(0,0,0,0.1)" class="clearfix"><span style="display:block; width: 20%; float: left; height: 7px; background: #fefefe"></span><span style="display:block; width: 80%; float: left; height: 7px; background: #fefefe"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #222"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin">Black</p>')
    $skinsList.append($skinBlack)
    var $skinPurple =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-purple" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div><span style="display:block; width: 20%; float: left; height: 7px;" class="bg-purple-active"></span><span class="bg-purple" style="display:block; width: 80%; float: left; height: 7px;"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #222d32"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin">Purple</p>')
    $skinsList.append($skinPurple)
    var $skinGreen =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-green" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div><span style="display:block; width: 20%; float: left; height: 7px;" class="bg-green-active"></span><span class="bg-green" style="display:block; width: 80%; float: left; height: 7px;"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #222d32"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin">Green</p>')
    $skinsList.append($skinGreen)
    var $skinRed =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-red" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div><span style="display:block; width: 20%; float: left; height: 7px;" class="bg-red-active"></span><span class="bg-red" style="display:block; width: 80%; float: left; height: 7px;"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #222d32"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin">Red</p>')
    $skinsList.append($skinRed)
    var $skinYellow =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-yellow" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div><span style="display:block; width: 20%; float: left; height: 7px;" class="bg-yellow-active"></span><span class="bg-yellow" style="display:block; width: 80%; float: left; height: 7px;"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #222d32"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin">Yellow</p>')
    $skinsList.append($skinYellow)

    // Light sidebar skins
    var $skinBlueLight =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-blue-light" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div><span style="display:block; width: 20%; float: left; height: 7px; background: #367fa9"></span><span class="bg-light-blue" style="display:block; width: 80%; float: left; height: 7px;"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #f9fafc"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin" style="font-size: 12px">Blue Light</p>')
    $skinsList.append($skinBlueLight)
    var $skinBlackLight =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-black-light" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div style="box-shadow: 0 0 2px rgba(0,0,0,0.1)" class="clearfix"><span style="display:block; width: 20%; float: left; height: 7px; background: #fefefe"></span><span style="display:block; width: 80%; float: left; height: 7px; background: #fefefe"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #f9fafc"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin" style="font-size: 12px">Black Light</p>')
    $skinsList.append($skinBlackLight)
    var $skinPurpleLight =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-purple-light" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div><span style="display:block; width: 20%; float: left; height: 7px;" class="bg-purple-active"></span><span class="bg-purple" style="display:block; width: 80%; float: left; height: 7px;"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #f9fafc"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin" style="font-size: 12px">Purple Light</p>')
    $skinsList.append($skinPurpleLight)
    var $skinGreenLight =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-green-light" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div><span style="display:block; width: 20%; float: left; height: 7px;" class="bg-green-active"></span><span class="bg-green" style="display:block; width: 80%; float: left; height: 7px;"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #f9fafc"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin" style="font-size: 12px">Green Light</p>')
    $skinsList.append($skinGreenLight)
    var $skinRedLight =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-red-light" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div><span style="display:block; width: 20%; float: left; height: 7px;" class="bg-red-active"></span><span class="bg-red" style="display:block; width: 80%; float: left; height: 7px;"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #f9fafc"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin" style="font-size: 12px">Red Light</p>')
    $skinsList.append($skinRedLight)
    var $skinYellowLight =
        $('<li />', { style: 'float:left; width: 33.33333%; padding: 5px;' })
        .append('<a href="javascript:void(0)" data-skin="skin-yellow-light" style="display: block; box-shadow: 0 0 3px rgba(0,0,0,0.4)" class="clearfix full-opacity-hover">' +
            '<div><span style="display:block; width: 20%; float: left; height: 7px;" class="bg-yellow-active"></span><span class="bg-yellow" style="display:block; width: 80%; float: left; height: 7px;"></span></div>' +
            '<div><span style="display:block; width: 20%; float: left; height: 20px; background: #f9fafc"></span><span style="display:block; width: 80%; float: left; height: 20px; background: #f4f5f7"></span></div>' +
            '</a>' +
            '<p class="text-center no-margin" style="font-size: 12px">Yellow Light</p>')
    $skinsList.append($skinYellowLight)

    $demoSettings.append('<h4 class="control-sidebar-heading">Skins</h4>')
    $demoSettings.append($skinsList)

    $tabPane.append($demoSettings)
    $('#control-sidebar-home-tab').after($tabPane)

    setup()

    $('[data-toggle="tooltip"]').tooltip()

    var client = new $.RestClient('/api/');
    client.add('environments');
    client.environments.read().done(function(data) {
        $.each(data.environments, function(key, obj) {
            $('#jinjamator_environment').append(new Option(obj.name, obj.path))
        });
    });
})

var client = new $.RestClient('/api/');
client.add('tasks');
client.add('jobs');
client.add('plugins', { isSingle: true });

client.plugins.add('output');


function update_breadcrumb(level1, level2) {
    $('.content-header-big').html(level1 + "<small class='content-header-small'>" + level2 + "</small>");
    $('.breadcrumb').html('<li><a href="#"><i class="fa fa-dashboard"></i>Home</a></li><li><a href="#">' + level1 + '</a></li><li class="active">' + level2 + '</li>')
}



function list_tasks(parent) {
    $(".treeview-item").removeClass("active")
    parent.parents('li').addClass('active');
    update_breadcrumb('Tasks', 'List');

    $.get("static/templates/main_content_section.html", function(data) {
        $(".all-content").html('<section class="content">' + data + '</section>');
    });

    client.tasks.read().done(function(data) {
        table_data = '<div class="box-body"><table id="task_list" class="table table-bordered table-hover">\
         <thead><tr><th>Task</th><th width="60%">Description</th><th width="1%">Actions</th></tr></thead>'
        data.tasks.forEach(function(value, index, array) {
            table_data += '<tr><td>' + value + '</td><td width="60%">not implemented yet</td>\
            <td align="right" width="1%" style="white-space:nowrap;">\
            <div class="icon">\
            <a href="#" class="fa fa-calendar schedule-href">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
            <a href="#" class="fa fa-edit">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
            <a href="#" class="fa fa-info-circle"></a>\
            </a></div>\
            </td></tr>'
        });

        table_data += '</table></div>';
        $(".main-content-box-title").replaceWith('<h3 class="box-title">Available Jinjamator tasks</h3>');
        $(".main-content-box").replaceWith(table_data);


        if ($.fn.dataTable.isDataTable('#task_list')) {
            $('#task_list').DataTable().destroy();
        }

        table = $('#task_list').DataTable({
                "lengthMenu": [
                    [15, 30, 100, -1],
                    [15, 30, 100, "All"]
                ]

            })
            //table.on( 'dblclick', function () {
        table.on('dblclick', 'tbody tr', function() {
            create_job(parent, table.row(this).data()[0]);
        });

        $('.main-section').removeClass('hidden');

    });
}

function create_job(parent, job_path, pre_defined_vars) {
    if (!job_path) {
        list_tasks(parent);
        return true;
    }
    if (!pre_defined_vars) {
        pre_defined_vars = {}
    }

    $(".treeview-item").removeClass("active")
    if (parent) {

        parent.parents('li').addClass('active');
    }
    update_breadcrumb('Jobs', 'Create');
    $.get("static/templates/main_content_section.html", function(data) {
        $(".all-content").html('<section class="content">' + data + '</section>');
        $(".main-content-box").replaceWith(`<div id="form"></div><script type="text/x-handlebars-template" id="ationbar">
        {{#if options.hideActionBar}}
        <div class="alpaca-array-actionbar alpaca-array-actionbar-{{actionbarStyle}} btn-group" data-alpaca-array-actionbar-parent-field-id="{{parentFieldId}}" data-alpaca-array-actionbar-field-id="{{fieldId}}" data-alpaca-array-actionbar-item-index="{{itemIndex}}">
          {{#each actions}}
          <button class="alpaca-array-actionbar-action {{../view.styles.smallButton}}" data-alpaca-array-actionbar-action="{{action}}">
                  {{#if this.iconClass}}
                  <i class="{{this.iconClass}}"></i>
                  {{/if}}
                  {{#if label}}{{{label}}}{{/if}}
              </button> {{/each}}
        </div>
        {{/if}}
      </script>`);

        client.tasks.read(job_path, {}, { 'data': JSON.stringify(pre_defined_vars), 'environment': $('#jinjamator_environment option:selected').val() }).done(function(data) {

            $.extend(data['view']['wizard'], {
                "buttons": {
                    "next": {
                        "click": function(e) {
                            control = $('#form').alpaca('get');

                            if ($('li.active[data-alpaca-wizard-step-index]')[0].getAttribute('data-alpaca-wizard-step-index') == 0) {
                                defaults_step = $('[data-alpaca-wizard-role="step"]')[1];

                                required_vars = {}
                                $.each(data['view']['wizard']['bindings'], function(key, value) {
                                    if (value == 1) {
                                        required_vars[key] = $('[name="' + key + '"]').val();
                                    }
                                });
                                client.tasks.read(job_path, {}, { 'data': JSON.stringify(required_vars), 'environment': $('#jinjamator_environment option:selected').val() }, ).done(function(data) {


                                    $.each(data['view']['wizard']['bindings'], function(key, value) {
                                        if (value == 2) {
                                            form_item = control.getControlByPath("/" + key);
                                            if (form_item === undefined) {

                                                control.createItem(key, data['schema']['properties'][key], data['options']['fields'][key], data['data'][key], 0, function(item) {
                                                    control.registerChild(item, 1);
                                                    defaults_step.append(item.containerItemEl[0]);


                                                });

                                            } else {
                                                form_item.setValue(data['data'][key]);
                                                form_item.refresh();
                                            }

                                        }
                                    });
                                });
                            }
                        }
                    },
                    "submit": {
                        "click": function() {
                            client.opts['stringifyData'] = true;
                            var data = this.getValue();
                            console.dir(data);
                            var task = data['task'];
                            delete data['task'];
                            $.each(data['output_plugin_parameters'], function(index) {
                                $.each(data['output_plugin_parameters'][index], function(key, value) {
                                    data[key] = value;
                                });
                            });
                            $.each(data['custom_parameters'], function(index) {
                                data[data['custom_parameters'][index]['key']] = data['custom_parameters'][index]['value'];
                            });
                            delete data['output_plugin_parameters'];
                            delete data['custom_parameters'];
                            var request_data = {
                                ['task']: task,
                                ['configuration']: data
                            }

                            console.dir(request_data);
                            client.jobs.create(request_data).done(function(data) {
                                //console.log(JSON.stringify(data));
                                setTimeout(function() { show_job(data['job_id']); }, 500); //this is ugly replace by subsequent api calls to check if job is queued
                            });


                        }
                    }
                }
            });
            data['options']['fields']['output_plugin']['onFieldChange'] = function(e) {


                var control = $("#form").alpaca("get");

                self = control.getControlByPath("/output_plugin_parameters");

                $.each(self.children, function(key, value) {
                    self.removeItem(0);
                });

                form_data = control.getValue();

                $.each(form_data['custom_parameters'], function(index) {
                    form_data[form_data['custom_parameters'][index]['key']] = form_data['custom_parameters'][index]['value'];
                });



                client.plugins.output.read(this.getValue(e), {}, form_data).done(function(data) {
                    order = {}
                    $.each(data['options']['fields'], function(key, value) {
                        order[value.order] = key;
                    });

                    $.each(order, function(index, var_name) {
                        var obj = Object({
                            'type': 'object',
                            'properties': {}
                        });
                        var options = Object({
                            'validator': false,

                        });

                        obj.properties[var_name] = data['schema']['properties'][var_name];
                        if (typeof(data['options']) !== 'undefined') {
                            if (typeof(data['options']['validator']) !== 'undefined') {
                                if (typeof(data['options']['validator'][var_name]) !== 'undefined') {
                                    options['validator'] = new Function("return " + data['options']['validator'][var_name].replace(/(\r\n|\n|\r)/gm, ""))();
                                }
                            }
                        };

                        //Object.assign(options,data['options']['fields'][var_name]);
                        //alert(JSON.stringify(options));
                        //Object.assign(data,{'options':{'fields':{var_name:{'hideActionBar':true}}}});
                        self.addItem(0, obj, options, '', function(item) {});
                    });
                });





            }
            data.options['allowNull'] = true;
            $("#form").alpaca(data);

            $('.main-content-box-title').remove();
            $('.main-section').removeClass('hidden');
        });





    });

}

function clone_job(job_id) {
    client.jobs.read(job_id).done(function(data) {
        var timestamp = Object.keys(data['log'][0])[0];
        var configuration = data['log'][0][timestamp]['configuration'];
        if (configuration.jinjamator_job_id !== undefined) {
            delete configuration.jinjamator_job_id;
        }

        create_job(false, data['jinjamator_task'], configuration);
    });


}

function undo_job(job_id) {
    client.jobs.read(job_id).done(function(data) {
        var timestamp = Object.keys(data['log'][0])[0];
        var configuration = data['log'][0][timestamp]['configuration'];
        configuration['undo'] = true;
        create_job(false, data['jinjamator_task'], configuration);
    });
}

function badge_color_from_state(state) {
    badge_color = '';
    if (state == 'FAILURE')
        badge_color = 'bg-red';
    if (state == 'ERROR')
        badge_color = 'bg-red';
    if (state == 'SUCCESS')
        badge_color = 'bg-green';
    if (state == 'PENDING')
        badge_color = 'bg-grey';
    if (state == 'WARNING')
        badge_color = 'bg-yellow';
    if (state == 'PROGRESS')
        badge_color = 'bg-blue';
    return badge_color;
}

function list_jobs(parent) {
    update_breadcrumb('Jobs', 'List');
    $(".treeview-item").removeClass("active")
    parent.parents('li').addClass('active');
    $.get("static/templates/main_content_section.html", function(data) {
        $(".all-content").html('<section class="content">' + data + '</section>');
    });

    client.jobs.read().done(function(data) {
        table_data = '<div class="box-body">\
            <table id="list_jobs" class="table table-bordered table-hover">\
                <thead>\
                <tr>\
                    <th width="1%">#</th>\
                    <th>Scheduled</th>\
                    <th>Start</th>\
                    <th>End</th>\
                    <th>ID</th>\
                    <th>Task</th>\
                    <th width="1%">Status</th>\
                </tr>\
                </thead>'
        $.each(data, function(i, item) {
            $.each(data[i], function(j, obj) {

                badge_color = badge_color_from_state(obj.state);
                table_data += '<tr><td width="1%">' + obj.id + '</td>\
                <td width="13%">' + obj.date_scheduled + '</td>\
                <td width="13%">' + obj.date_start + '</td>\
                <td width="13%">' + obj.date_done + '</td>\
                <td width="17%">' + obj.task_id + '</td>\
                <td>' + obj.task + '</td>\
                <td width="1%"><span class="badge ' + badge_color + '">' + obj.state + '</span></td></tr>'
            })
        });
        table_data += '</table></div>';
        $(".main-content-box-title").replaceWith('<h3 class="box-title">Job History</h3>');
        $(".main-content-box").replaceWith(table_data);


        if ($.fn.dataTable.isDataTable('#list_jobs')) {
            $('#list_jobs').DataTable().destroy();
        }

        table = $('#list_jobs').DataTable({
            "lengthMenu": [
                [15, 30, 100, -1],
                [15, 30, 100, "All"]
            ],
            "order": [
                [0, "desc"]
            ]
        })

        table.on('dblclick', 'tbody tr', function() {
            show_job(table.row(this).data()[4]);
        });

        $('.main-section').removeClass('hidden');
    });

}


function set_timeline_loglevel(level) {
    var levels = {
        'DEBUG': 4,
        'INFO': 3,
        'WARNING': 2,
        'ERROR': 1,
        'TASKLET_RESULT': 0
    }

    $(".timeline-item-list-item").each(function() {
            cur_level = $(this).find('#log_level').html()
            if (levels[cur_level] > levels[level]) {
                $(this).addClass('hidden');
            } else {
                $(this).removeClass('hidden');
            }
        }

    );

}


function update_timeline(job_id) {
    client.jobs.read(job_id).done(function(data) {

        timeline_render_elements(data);
        if ($('#job_id').length > 0) {
            setTimeout(update_timeline, 1000, job_id);
        }
    });

}

function timeline_render_elements(data) {
    var last_task = '';
    var timeline = $('.timeline');
    var rendered_timestamps = $.makeArray($('.time').map(function() {
        return this.innerHTML;
    }));
    $('#job_status').html(data['state']);
    $('#job_status').addClass("badge");
    $('#job_status').addClass(badge_color_from_state(data['state']));


    $.each(data['log'], function(index, log_item) {
        var timestamp = Object.keys(log_item)[0];

        if (!rendered_timestamps.includes(timestamp)) {


            if (last_task != log_item[timestamp]['current_task']) {
                var timeline_label = timeline_templates.filter('#timeline-label-template');
                timeline_label.find('.time-label span').addClass('bg-blue');
                timeline_label.find('.time-label span').html(log_item[timestamp]['current_task']);
                timeline.append(timeline_label.html());
            }


            var timeline_item = timeline_templates.filter('#timeline-content-template').clone(true);

            switch (log_item[timestamp]['level']) {
                case 'INFO':
                    timeline_item.find('.timeline-icon').addClass('bg-blue');
                    timeline_item.find('.timeline-icon').addClass('fa-info');

                    break;
                case 'WARNING':
                    timeline_item.find('.timeline-icon').addClass('bg-yellow');
                    timeline_item.find('.timeline-icon').addClass('fa-exclamation-triangle');

                    break;
                case 'ERROR':
                    timeline_item.find('.timeline-icon').addClass('bg-red');
                    timeline_item.find('.timeline-icon').addClass('fa-thumbs-down');
                    break;
                case 'DEBUG':
                    timeline_item.find('.timeline-icon').addClass('bg-grey');
                    timeline_item.find('.timeline-icon').addClass('fa-bug');
                    timeline_item.find('.timeline-item-list-item').addClass('hidden');
                    break;
                case 'TASKLET_RESULT':
                    timeline_item.find('.timeline-icon').addClass('bg-green');
                    timeline_item.find('.timeline-icon').addClass('fa-check-square');

                    break;
            }


            timeline_item.find('.time').html(timestamp);
            if (log_item[timestamp]['message'].length > (105 - log_item[timestamp]['current_tasklet'].length))
                var short_msg = log_item[timestamp]['message'].slice(0, (104 - log_item[timestamp]['current_tasklet'].length)) + '...';
            else
                var short_msg = log_item[timestamp]['message'];



            timeline_item.find('.timeline-header').html('<strong>' + log_item[timestamp]['current_tasklet'] + ':</strong> ' + short_msg);


            timeline_item.find('#configuration').html('<div style="white-space: pre-wrap;">' + JSON.stringify(log_item[timestamp]['configuration'], null, 4) + '</div>');
            timeline_item.find('#configuration').attr('id', 'configuration_' + index);
            timeline_item.find('#nav_configuration').attr('href', '#configuration_' + index);

            timeline_item.find('#overview').attr('id', 'overview_' + index);
            timeline_item.find('#nav_overview').attr('href', '#overview_' + index);

            timeline_item.find('#raw_log').html('<div style="white-space: pre-wrap;">' + JSON.stringify(log_item[timestamp], null, 4) + '</div>');
            timeline_item.find('#raw_log').attr('id', 'raw_log_' + index);
            timeline_item.find('#nav_raw_log').attr('href', '#raw_log_' + index);

            timeline_item.find('#output_plugin').html(log_item[timestamp]['configuration']['output_plugin']);
            timeline_item.find('#log_level').html(log_item[timestamp]['level']);
            timeline_item.find('#current_task').html(log_item[timestamp]['current_task']);
            timeline_item.find('#current_tasklet').html(log_item[timestamp]['current_tasklet']);
            if (!log_item[timestamp]['parent_tasklet'])
                timeline_item.find('#parent_tasklet').html('None');
            else
                timeline_item.find('#parent_tasklet').html(log_item[timestamp]['parent_tasklet']);

            if (!log_item[timestamp]['parent_task'])
                timeline_item.find('#parent_task').html('None');
            else
                timeline_item.find('#parent_task').html(log_item[timestamp]['parent_task']);

            timeline_item.find('#console_output').html('<div style="white-space: pre-wrap;">' + log_item[timestamp]['stdout'] + '</div>');
            timeline_item.find('#full_message').html('<div style="white-space: pre-wrap;">' + log_item[timestamp]['message'] + '</div>');

            //timeline_item.insertAfter($('#timeline_overview'));
            timeline.append(timeline_item.html());
        }
        last_task = log_item[timestamp]['current_task'];

    });

}

function show_job(job_id) {
    update_breadcrumb('Jobs', 'Detail');
    $.get("static/templates/main_content_section.html", function(data) {
        $(".all-content").html('<section class="content">' + data + '</section>');

        $.get("static/templates/timeline.html", function(data) {
            timeline_templates = $(data);
            var timeline = timeline_templates.filter('#timeline-template');
            var timeline_overview_box = timeline_templates.filter('#timeline-overview-box-template');
            timeline_overview_box.find('#job_id').html(job_id);

            timeline.find('.timeline').append(timeline_overview_box.html());
            $(".all-content").html('<section class="content">' + timeline.html() + '</section>');

            client.jobs.read(job_id).done(function(data) {

                timeline_render_elements(data);
                $("#job_path").html(data['jinjamator_task']);
            });


            $('.main-section').removeClass('hidden');
            setTimeout(update_timeline, 1000, job_id);


        });

    });


}