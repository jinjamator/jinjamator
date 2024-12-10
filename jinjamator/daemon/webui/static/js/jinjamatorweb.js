var update_output_plugin = true;
var log_levels = {
    'DEBUG': 4,
    'INFO': 3,
    'WARNING': 2,
    'ERROR': 1,
    'TASKLET_RESULT': 0
}



$(function () {
    'use strict'

    /**
     * Get access to plugins
     */

    $('[data-toggle="control-sidebar"]').controlSidebar()
    $('[data-toggle="push-menu"]').pushMenu()
    var $pushMenu = $('[data-toggle="push-menu"]').data('lte.pushmenu')
    var $controlSidebar = $('[data-toggle="control-sidebar"]').data('lte.controlsidebar')
    var $layout = $('body').data('lte.layout')
    $(window).on('load', function () {
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
        'skin-yellow',
        'skin-blue',
        'skin-black',
        'skin-red',
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
        if (typeof (Storage) !== 'undefined') {
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
        if (typeof (Storage) !== 'undefined') {
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
        $.each(mySkins, function (i) {
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
        set_jinjamator_version()
        var tmp = get('skin')
        if (tmp && $.inArray(tmp, mySkins))
            changeSkin(tmp)
        else
            changeSkin('skin-yellow')


        // Add the change skin listener
        $('[data-skin]').on('click', function (e) {
            if ($(this).hasClass('knob'))
                return
            e.preventDefault()
            changeSkin($(this).data('skin'))
        })

        // Add the layout manager
        $('[data-layout]').on('click', function () {
            changeLayout($(this).data('layout'))
        })

        $('[data-controlsidebar]').on('click', function () {
            changeLayout($(this).data('controlsidebar'))
            var slide = !$controlSidebar.options.slide

            $controlSidebar.options.slide = slide
            if (!slide)
                $('.control-sidebar').removeClass('control-sidebar-open')
        })

        $('[data-sidebarskin="toggle"]').on('click', function () {
            var $sidebar = $('.control-sidebar')
            if ($sidebar.hasClass('control-sidebar-dark')) {
                $sidebar.removeClass('control-sidebar-dark')
                $sidebar.addClass('control-sidebar-light')
            } else {
                $sidebar.removeClass('control-sidebar-light')
                $sidebar.addClass('control-sidebar-dark')
            }
        })

        $('[data-enable="expandOnHover"]').on('click', function () {
            $(this).attr('disabled', true)
            $pushMenu.expandOnHover()
            if (!$('body').hasClass('sidebar-collapse'))
                $('[data-layout="sidebar-collapse"]').click()
        })


        $('#jinjamator_environment').on('change', function () {
            store('jinjamator_environment', this.value)
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
        'id': 'control-sidebar-options-tab',
        'class': 'tab-pane active'
    })


    // Create the menu
    var $Settings = $('<div />')


    $tabPane.append($Settings)
    $('#control-sidebar-home-tab').after($tabPane)

    setup()

    $('[data-toggle="tooltip"]').tooltip()

    $('.render_username').each(function () { this.innerHTML = sessionStorage.getItem('logged_in_username'); })
    var client = new $.RestClient('/api/');
    client.add('environments');
    let cur_env = get('jinjamator_environment');
    client.environments.read().done(function (data) {
        $.each(data.environments, function (key, environment) {
            $.each(environment.sites, function (key, site) {
                let env_name = environment.name + '/' + site.name;
                let select = false;
                if (cur_env == env_name) {
                    select = true;
                }
                $('#jinjamator_environment').append(new Option(env_name, env_name, select, select))
            });
        });
    });
})


class SmoothOverlay {
    constructor(overlay_selector = "#overlay") {
        this.overlay_selector = overlay_selector
        this.overlay = $(this.overlay_selector)
        this.usage_count = 0
    }

    fadeIn(msec) {
        // log.debug("SmoothOverlay","fadeIn",msec)
        if (this.usage_count <= 0) {
            this.usage_count = 0
            $(this.overlay_selector).fadeIn(msec)
        }
        this.usage_count++
    }
    fadeOut(msec, ignore = false) {
        // log.debug("SmoothOverlay","fadeOut",msec)
        this.usage_count--
        if ((this.usage_count == 0) && (ignore == false)) {
            $(this.overlay_selector).fadeOut(msec)
        }
    }
    reset() {
        this.fadeOut();
        this.usage_count = 0
        
    }
}

class logging {
    static CRITICAL = 50
    static ERROR = 40
    static WARNING = 30
    static INFO = 20
    static DEBUG = 10
    static FE_DEBUG = 9
    static NOTSET = 0

    constructor(level = logging.INFO) {
        this.level = level;
        this._init()
        this.prefix = ""
    }

    _init() {

        if (console.log.bind === "undefined") {
            // IE < 10

            this.error = Function.prototype.bind.call(console.error, console, `[E] ${this.prefix}:`);
            this.warning = Function.prototype.bind.call(console.warn, console, `[W] ${this.prefix}:`);
            this.warn = Function.prototype.bind.call(console.warn, console, `[W] ${this.prefix}:`);
            this.info = Function.prototype.bind.call(console.info, console, `[I] ${this.prefix}:`);
            this.debug = Function.prototype.bind.call(console.debug, console, `[D] ${this.prefix}:`);
            this.fe_debug = Function.prototype.bind.call(console.debug, console, `[D] ${this.prefix}:`);
            this.dir = Function.prototype.bind.call(console.dir, console, `[D] ${this.prefix}:`);
            this.table = Function.prototype.bind.call(console.table, console, `[D] ${this.prefix}:`);

        } else {
            this.error = console.error.bind(console, `[E] ${this.prefix}:`);
            this.warning = console.warn.bind(console, `[W] ${this.prefix}:`);
            this.warn = console.warn.bind(console, `[W] ${this.prefix}:`);
            this.info = console.info.bind(console, `[I] ${this.prefix}:`);
            this.debug = console.debug.bind(console, `[D] ${this.prefix}:`);
            this.fe_debug = console.debug.bind(console, `[D] ${this.prefix}:`);
            this.dir = console.dir.bind(console, `[D] ${this.prefix}:`);
            this.table = console.table.bind(console, `[D] ${this.prefix}:`);
        }
        if (this.level > logging.ERROR) {
            this.error = function () { return };
        }
        if (this.level > logging.WARNING) {
            this.warn = function () { return };
            this.warning = function () { return };
        }
        if (this.level > logging.INFO) {
            this.info = function () { return };
        }
        if (this.level > logging.DEBUG) {
            this.debug = function () { return };
            this.dir = function () { return };
            this.table = function () { return };
        }
        if (this.level > logging.FE_DEBUG) {
            this.fe_debug = function () { return };
        }
        if (this.level <= logging.NOTSET) {
            this.fe_debug = function () { return };
            this.debug = function () { return };
            this.dir = function () { return };
            this.table = function () { return };
            this.info = function () { return };
            this.warn = function () { return };
            this.warning = function () { return };
            this.error = function () { return };
        }

    }

    setLevel(level) {
        this.level = level;
        this._init();
    }

    setPrefix(prefix) {
        this.prefix = `[${prefix}]`
        this._init();
    }

}




const log = new logging(logging.ERROR)
const wizard_overlay = new SmoothOverlay()
const client = new $.RestClient('/api/', { stringifyData: true });


client.add('tasks');
client.add('jobs');
client.add('plugins', { isSingle: true });
client.add('aaa', { isSingle: true });
client.aaa.add('providers', { isSingle: true });
client.aaa.add('users');
client.aaa.add('roles');
client.aaa.users.add('roles', { isSingle: true });
client.plugins.add('output');







function update_breadcrumb(level1, level2) {
    $('.content-header-big').html(level1 + "<small class='content-header-small'>" + level2 + "</small>");
    $('.breadcrumb').html('<li><a href="#"><i class="fa fa-dashboard"></i>Home</a></li><li><a href="#">' + level1 + '</a></li><li class="active">' + level2 + '</li>')
}

function logout() {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('logged_in_username');
    location.href = '/login.html';
}

function list_roles() {

    // $(".treeview-item").removeClass("active")
    // parent.parents('li').addClass('active');
    update_breadcrumb('AAA', 'Roles');

    $.get("static/templates/main_content_section.html", function (data) {
        $(".all-content").html('<section class="content">' + data + '</section>');
    });

    client.aaa.roles.read().done(function (data) {
        table_data = '<div class="box-body"><table id="roles_list" class="table table-bordered table-hover">\
         <thead><tr><th>ID</th><th width="99%">Role Name</th><th width="1%">Actions</th></tr></thead>'

        data.forEach(function (value, index, array) {
            table_data += '<tr><td>' + value.id + '</td><td width="99%">' + value.name + '</td>\
            <td align="center" width="1%" style="white-space:nowrap;">\
            <div class="icon">\
            <a href="#" class="fa fa-remove delete-role-href" onclick="delete_role(\'' + value.id + '\')">\
            <!-- <a href="#" class="fa fa-delete">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
            <a href="#" class="fa fa-info-circle"></a>-->\
            </a></div> \
            </td></tr > '
        });

        table_data += '</table></div>';
        $(".main-content-box-title").replaceWith('<h3 class="box-title">Roles</h3>');
        $(".main-content-box").replaceWith(table_data);


        if ($.fn.dataTable.isDataTable('#task_list')) {
            $('#roles_list').DataTable().destroy();
        }

        table = $('#roles_list').DataTable({
            dom: 'Bfrtip',
            autoWidth: false,
            buttons: [
                {
                    text: 'Create Role',
                    action: function (e, dt, node, config) {
                        create_role();
                    }
                }
            ],
            "lengthMenu": [
                [15, 30, 100, -1],
                [15, 30, 100, "All"]
            ]

        })
        //table.on( 'dblclick', function () {
        // table.on('dblclick', 'tbody tr', function() {
        //     edit_user(table.row(this).data()[0]);
        // });

        $('.main-section').removeClass('hidden');

    });
}


function create_role() {
    update_breadcrumb('AAA', 'Roles');

    $(".all-content").html(`
    <section class="content">
    <div class="row">
    <!-- left column -->
    <div class="col-md-6">
    <div class="box box-primary">
        <div class="box-header with-border">
        <h3 class="box-title">Create Role</h3>
        </div>
        <!-- /.box-header -->
        <!-- form start -->
            <form role="form" id='create_role_form'>
            <div class="box-body">
            <div class="form-group">
            <label for="name">Rolename</label>
            <input type="string" class="form-control" id="role_name" placeholder="Name">
            </div>
        </div>
        <div class="box-footer">
            <button type="submit" class="btn btn-primary">Create Role</button>
        </div>
        </form>
    </div>
    <!-- /.box -->
    </div>
    </div>
    </section>`
    );



    $("#create_role_form").submit(function (e) {
        e.preventDefault();
        var form = this;
        role_data = {
            name: this.role_name.value
        }

        client.aaa.roles.create(role_data);
        list_roles();

    });
}


function delete_role(id) {
    client.aaa.roles.destroy(id).done(function (user_data) {
        list_roles();
    });
}

function delete_user(id) {
    client.aaa.users.destroy(id).done(function (user_data) {
        list_users();
    });
}

function edit_user(username) {

    update_breadcrumb('AAA', 'Users');
    client.aaa.users.read(username).done(function (user_data) {
        client.aaa.roles.read().done(function (roledata) {
            var select_data = [];

            $(".all-content").html(
                `<section class="content">
            <div class="row">
            <!-- left column -->
            <div class="col-md-6">
            <div class="box box-primary">
                <div class="box-header with-border">
                <h3 class="box-title">Edit User</h3>
                </div>
                <!-- /.box-header -->
                <!-- form start -->
                    <form role="form" id='edit_user_form'>
                    <div class="box-body">
                    <div class="form-group">
                    <label for="username">Username</label>
                    <input type="string" class="form-control" id="username" placeholder="Username" disabled value='` + user_data.username + `'>
                    </div>
                    <div class="form-group">
                    <label for="full_name">Full Name</label>
                    <input type="string" class="form-control" id="full_name" placeholder="Full Name" value='` + user_data.name + `'>
                    </div>
                    <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" class="form-control" id="password" placeholder="Password">
                    </div>
                    <div class="form-group">
                    <label for="roles">Roles</label>
                    <select class="form-control" id="roles" multiple></select>
                    </div>                    
                    
                </div>
                <div class="box-footer">
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </div>
                </form>
            </div>
            <!-- /.box -->
            </div>
            </div>
            </section>`
            );
            var selected = [];
            user_data.roles.forEach(function (value, index, array) {
                selected.push(value.id);
            });

            roledata.forEach(function (value, index, array) {
                is_selected = false;
                if (selected.includes(value.id)) {
                    is_selected = true;
                }

                $('#roles').append($('<option>', { value: value.name, text: value.name, selected: is_selected }));
            });
            $('#roles').multiselect({
                enableFiltering: true,
                filterBehavior: 'value', maxHeight: 400, includeSelectAllOption: true
            });
            $("#edit_user_form").submit(function (e) {
                e.preventDefault();
                var form = this;
                if (this.password.value != null) {
                    user_data.password = this.password.value;
                }
                user_data.name = this.full_name.value;
                new_role_data = [];
                for (let item of this.roles.selectedOptions) {
                    new_role_data.push(item.value);
                }
                user_data.roles = new_role_data;
                console.dir(user_data)
                client.aaa.users.update(username, user_data);
                list_users();
            });
        });
    });

}

function create_user() {

    update_breadcrumb('AAA', 'Users');

    client.aaa.roles.read().done(function (roledata) {
        user_data = {}
        var select_data = [];

        $(".all-content").html(
            `<section class="content">
            <div class="row">
            <!-- left column -->
            <div class="col-md-6">
            <div class="box box-primary">
                <div class="box-header with-border">
                <h3 class="box-title">Create User</h3>
                </div>
                <!-- /.box-header -->
                <!-- form start -->
                    <form role="form" id='create_user_form'>
                    <div class="box-body">
                    <div class="form-group">
                    <label for="username">Username</label>
                    <input type="string" class="form-control" id="username" placeholder="Username">
                    </div>
                    <div class="form-group">
                    <label for="full_name">Full Name</label>
                    <input type="string" class="form-control" id="full_name" placeholder="full_name">
                    </div>
                    <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" class="form-control" id="password" placeholder="Password">
                    </div>
                    <div class="form-group">
                    <label for="aaa_provider">AAA Provider</label>
                    <select class="form-control" id="aaa_provider"></select>
                    </div>                    

                    <div class="form-group">
                    <label for="roles">Roles</label>
                    <select class="form-control" id="roles" multiple></select>
                    </div>                    
                    
                </div>
                <div class="box-footer">
                    <button type="submit" class="btn btn-primary">Create User</button>
                </div>
                </form>
            </div>
            <!-- /.box -->
            </div>
            </div>
            </section>`
        );


        roledata.forEach(function (value, index, array) {
            $('#roles').append($('<option>', { value: value.name, text: value.name }));
        });

        client.aaa.providers.read().done(function (providers) {
            providers.forEach(function (value, index, array) {
                $('#aaa_provider').append($('<option>', { value: value.name, text: value.display_name }));
            });
            $('#aaa_provider').multiselect({
                enableFiltering: true,
                filterBehavior: 'value', maxHeight: 400, includeSelectAllOption: true
            });

        });

        $('#roles').multiselect({
            enableFiltering: true,
            filterBehavior: 'value', maxHeight: 400, includeSelectAllOption: true
        });

        $("#create_user_form").submit(function (e) {
            e.preventDefault();
            var form = this;
            if (this.password.value != null) {
                user_data.password = this.password.value;
            }
            user_data.name = this.full_name.value;
            user_data.username = this.username.value;
            new_role_data = [];
            for (let item of this.roles.selectedOptions) {
                new_role_data.push(item.value);
            }
            user_data.roles = new_role_data;

            client.aaa.users.create(user_data);
            list_users();
        });
    });


}


function list_users() {

    // $(".treeview-item").removeClass("active")
    // parent.parents('li').addClass('active');
    update_breadcrumb('AAA', 'Users');

    $.get("static/templates/main_content_section.html", function (data) {
        $(".all-content").html('<section class="content">' + data + '</section>');
    });

    client.aaa.users.read().done(function (data) {
        table_data = '<div class="box-body"><table id="users_list" class="table table-bordered table-hover">\
         <thead><tr><th>ID</th><th>Username</th><th width="60%">Full Name</th><th>AAA Provider</th><th width="1%">Actions</th></tr></thead>'

        data.forEach(function (value, index, array) {
            table_data += '<tr><td>' + value.id + '</td><td>' + value.username + '</td><td width="60%">' + value.name + '</td> <td> ' + value.aaa_provider + ' </td>\
            <td align="center" width="1%" style="white-space:nowrap;">\
            <div class="icon">\
            <a href="#" class="fa fa-edit edit-user-href" onclick="edit_user(\'' + value.id + '\')">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
            <a href="#" class="fa fa-remove delete-user-href" onclick="delete_user(\'' + value.id + '\')">\
            </a></div> \
            </td></tr > '
        });

        table_data += '</table></div>';
        $(".main-content-box-title").replaceWith('<h3 class="box-title">Users</h3>');
        $(".main-content-box").replaceWith(table_data);


        if ($.fn.dataTable.isDataTable('#users_list')) {
            $('#users_list').DataTable().destroy();
        }

        table = $('#users_list').DataTable({
            dom: 'Bfrtip',
            autoWidth: false,
            buttons: [
                {
                    text: 'Create User',
                    action: function (e, dt, node, config) {
                        create_user();
                    }
                }
            ],
            "lengthMenu": [
                [15, 30, 100, -1],
                [15, 30, 100, "All"]
            ]

        })

        table.on('dblclick', 'tbody tr', function () {
            edit_user(table.row(this).data()[1]);
        });

        $('.main-section').removeClass('hidden');

    });
}


function list_tasks() {

    // $(".treeview-item").removeClass("active")
    // parent.parents('li').addClass('active');
    update_breadcrumb('Tasks', 'List');

    $.get("static/templates/main_content_section.html", function (data) {
        $(".all-content").html('<section class="content">' + data + '</section>');
    });

    client.tasks.read().done(function (data) {
        table_data = '<div class="box-body"><table id="task_list" class="table table-bordered table-hover">\
         <thead><tr><th>Task</th><th width="60%">Description</th><th width="1%">Actions</th></tr></thead>'
        data.tasks.forEach(function (value, index, array) {
            if (value.gui) {
                table_data += '<tr><td>' + value.path + '</td><td width="60%">' + value.description + '</td>\
                <td align="center" width="1%" style="white-space:nowrap;">\
                <div class="icon">\
                <a href="#" class="fa fa-calendar schedule-href" onclick="create_job(\'' + value.path + '\')">\
                <!-- <a href="#" class="fa fa-edit">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
                <a href="#" class="fa fa-info-circle"></a>-->\
                </a></div> \
                </td></tr > '
            }
        });

        table_data += '</table></div>';
        $(".main-content-box-title").replaceWith('<h3 class="box-title">Available Jinjamator tasks</h3>');
        $(".main-content-box").replaceWith(table_data);


        if ($.fn.dataTable.isDataTable('#task_list')) {
            $('#task_list').DataTable().destroy();
        }

        $.fn.dataTable.ext.search.pop() // dirty but is the only thing that works at the moment
        delete $.fn.DataTable.ext.order["alpaca"]
        table = $('#task_list').DataTable({
            autoWidth: false,
            "lengthMenu": [
                [15, 30, 100, -1],
                [15, 30, 100, "All"]
            ]

        })
        //table.on( 'dblclick', function () {



        table.on('dblclick', 'tbody tr', function () {
            create_job(table.row(this).data()[0]);
            table.destroy();

        });

        $('.main-section').removeClass('hidden');

    });
}

function create_job(job_path, pre_defined_vars) {
    if (!job_path) {
        list_tasks();
        return true;
    }
    wizard_overlay.reset();
    if (!pre_defined_vars) {
        pre_defined_vars = {}
    }

    if (("undo" in pre_defined_vars) && (pre_defined_vars.undo == true)){
        update_breadcrumb('Jobs', 'Undo ' + pre_defined_vars.__old_job_id__);
    }
    else if(("__clone__" in pre_defined_vars)) {
        update_breadcrumb('Jobs', 'Clone ' + pre_defined_vars.__old_job_id__ );
    }
    else{
        update_breadcrumb('Jobs', 'Create');
    }

    


    $.get("static/templates/main_content_section.html", function (data) {
        $(".all-content").html('<section class="content">' + data + '</section>');
        $(".main-content-box").replaceWith(`
        <div id="overlay">
            <div class="cv-spinner">
                <span class="spinner"></span>
            </div>
        </div>
        <div id="form" class="jinjamator-task-wizard">
        </div><script type="text/x-handlebars-template" id="ationbar">
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

        $.ajax({
            url: "/api/tasks/" + job_path + "/resources/js/form.js",
            dataType: "script",
            error: function () { }
        });


        client.tasks.read(job_path, {}, { 'preload-data': JSON.stringify(pre_defined_vars), 'preload-defaults-from-site': $('#jinjamator_environment option:selected').val() }).done(function (data) {

            $.extend(data['view']['wizard'], {
                "buttons": {
                    "next": {
                        "click": function (e) {
                            control = $('#form').alpaca('get');

                            if ($('li.active[data-alpaca-wizard-step-index]')[0].getAttribute('data-alpaca-wizard-step-index') == 0) {
                                defaults_step = $('[data-alpaca-wizard-role="step"]')[1];

                                required_vars = {}
                                $.each(data['view']['wizard']['bindings'], function (key, value) {
                                    if (value == 1) {
                                        required_vars[key] = $('[name="' + key + '"]').val();
                                    }
                                });
                                client.tasks.read(job_path, {}, { 'preload-data': JSON.stringify(required_vars), 'preload-defaults-from-site': $('#jinjamator_environment option:selected').val() },).done(function (data) {


                                    $.each(data['view']['wizard']['bindings'], function (key, value) {
                                        if (value == 2) {
                                            form_item = control.getControlByPath("/" + key);
                                            if (form_item === undefined) {

                                                control.createItem(key, data['schema']['properties'][key], data['options']['fields'][key], data['data'][key], 0, function (item) {
                                                    control.registerChild(item, 1);
                                                    defaults_step.append(item.containerItemEl[0]);


                                                });

                                            } else {
                                                if(!(key in required_vars)){
                                                    form_item.setValue(data['data'][key]);
                                                    form_item.refresh();
                                                }

                                            }

                                        }
                                    });
                                });
                            }
                        }
                    },
                    "submit": {
                        "click": function () {

                            client.opts['stringifyData'] = true;
                            url_data = { 'preload-defaults-from-site': $('#jinjamator_environment option:selected').val() }
                            var data = this.getValue();

                            var task = job_path;
                            delete data['task'];

                            for (property in data['output_plugin_parameters']) {
                                data[property] = data['output_plugin_parameters'][property];
                            }

                            for (property in data) {
                                if (property.startsWith('__no_vars_')) {
                                    delete data[property];
                                }
                                if (data[property] === null) {
                                    delete data[property];
                                }
                            }

                            delete data['output_plugin_parameters'];


                            if (('wizard_ask_before_submit' in data) && data['wizard_ask_before_submit'] === true) {

                                $('#modal-submit').modal('show')
                                $('#modal-submit ').find('.btn-ok').unbind('click')
                                $('#modal-submit ').find('.btn-ok').on('click', function () {
                                    client.tasks.create(job_path, data, url_data).done(function (data) {
                                        $('#modal-submit').modal('hide');
                                        wizard_overlay.fadeIn();
                                        setTimeout(function () { show_job(data['job_id']); }, 1000); //this is ugly replace by subsequent api calls to check if job is queued
                                    });
                                })
                            }
                            else {
                                wizard_overlay.fadeIn();
                                client.tasks.create(job_path, data, url_data).done(function (data) {
                                    setTimeout(function () { show_job(data['job_id']); }, 1000); //this is ugly replace by subsequent api calls to check if job is queued
                                });

                            }



                        }
                    }
                }
            });
            data['options']['fields']['output_plugin']['onFieldChange'] = function (e) {


                console.log("event,check", e)
                if (e.hasOwnProperty('originalEvent')) {
                    return true;
                }
                var control = $("#form").alpaca("get");
                form_data = control.getValue();

                output_plugin_parameters = control.getControlByPath("/output_plugin_parameters");
                // console.log(output_plugin_parameters)
                console.log(output_plugin_parameters)
                $.each(output_plugin_parameters.children, function (key, value) {
                    // console.log(0)
                    // console.log(output_plugin_parameters.children[key].propertyId)
                    if (typeof (output_plugin_parameters.children[0].propertyId) !== 'undefined') {
                        output_plugin_parameters.removeItem(output_plugin_parameters.children[0].propertyId, function () { });
                    }
                });



                client.plugins.output.read(this.getValue(e), {}, form_data).done(function (data) {
                    // console.log(data)
                    options = data['schema']['options'];
                    schema = data['schema']['schema'];


                    order = {}
                    $.each(options.fields, function (key, value) {
                        order[value.order] = key;
                    });

                    $.each(order, function (index, var_name) {


                        // data.properties[var_name] = data['schema']['properties'][var_name];
                        // if (typeof(options) !== 'undefined') {
                        //     if (typeof(options.fields.validator) !== 'undefined') {
                        //         if (typeof(options.fields[var_name].validator) !== 'undefined') {
                        //             options.fields[var_name].validator = new Function("return " + options.fields[var_name].validator.replace(/(\r\n|\n|\r)/gm, ""))();
                        //         }
                        //     }
                        // };

                        // console.log(output_plugin_parameters.children)
                        output_plugin_parameters.addItem(var_name, schema.properties[var_name], options.fields[var_name], '', function (item) { });
                    });
                    console.log(output_plugin_parameters)
                });





            }
            data.options['allowNull'] = true;


            data['postRender'] = function (control) {
                form_data = control.getValue();


                if ('output_plugin' in form_data) {
                    var output_plugin_name = form_data['output_plugin'];
                } else {
                    console.log('output_plugin undefined defaulting to console');
                    var output_plugin_name = 'console';

                }


                client.plugins.output.read(output_plugin_name, {}, form_data).done(function (data) {
                    var itemId = "output_plugin_parameters";
                    var itemSchema = data['schema']['schema']
                    var itemOptions = data['schema']['options']

                    var insertAfterId = "output_plugin";
                    output_plugin = $('[data-alpaca-field-name="output_plugin"]')[0];
                    // console.dir(output_plugin)

                    control.createItem(itemId, itemSchema, itemOptions, {}, '', function (item) {
                        control.registerChild(item, 3);
                        output_plugin.parentNode.append(item.containerItemEl[0]);

                    });

                });


                if ('post_render' in data) {
                    // console.log(data['post_render'])
                    window[data['post_render']](control)
                }
            };
            var step_counter = [0, 0, 0]
            $.each(data['view']['wizard']['bindings'], function (key, value) {
                step_counter[value - 1]++;
            });
            step_counter.forEach(function (value, index, array) {
                if (value == 0) {
                    var step = index + 1;
                    data['schema']['properties']['__no_vars_' + step] = {
                        'required': false,
                        'title': 'No variables',
                        'type': "string",
                        'readonly': true
                    }
                    data['view']['wizard']['bindings']['__no_vars_' + step] = step

                }
            });



            $("#form").alpaca(data);





            $('.main-content-box-title').remove();
            $('.main-section').removeClass('hidden');
        });





    });

}

function clone_job(job_id, undo) {
    wizard_overlay.fadeIn()
    
    client.jobs.read(job_id).done(function (data) {
        var timestamp = Object.keys(data['log'][0])[0];
        var configuration = data['log'][0][timestamp]['configuration'];
        

        if (undo) {
            configuration["undo"] = true;
        }
        if (configuration.jinjamator_job_id !== undefined) {
            
            delete configuration.jinjamator_job_id;
        }
        if (data.files.length > 0) {
            data['files'].forEach(function (value, index, array) {
                if (configuration["filenames"]){
                configuration["filenames"].forEach(function (form_data, form_index, form_array) {
                    if (form_data.name == value) {
                        configuration["filenames"][form_index].filesystem_path = data.id + '/' + value
                    }
                
                });
            }

            });
        }
        configuration["__clone__"]=true;
        configuration["__old_job_id__"]= job_id;
        create_job(data['jinjamator_task'], configuration);
        wizard_overlay.fadeOut()
    });


}

function undo_job(job_id) {
    clone_job(job_id, true);
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
    if (state == 'DEBUGGING')
        badge_color = 'bg-orange';
    return badge_color;
}

function list_jobs() {
    update_breadcrumb('Jobs', 'History');
    $(".treeview-item").removeClass("active")
    // parent.parents('li').addClass('active');
    $.get("static/templates/main_content_section.html", function (data) {
        $(".all-content").html('<section class="content">' + data + '</section>');
    });

    client.jobs.read().done(function (data) {
        table_data = '<div class="box-body">\
            <table id="list_jobs" class="table table-bordered table-hover">\
                <thead>\
                <tr>\
                    <th width="1%">#</th>\
                    <th>Created by</th>\
                    <th>Scheduled</th>\
                    <th>Start</th>\
                    <th>End</th>\
                    <th>ID</th>\
                    <th>Task</th>\
                    <th width="1%">Status</th>\
                </tr>\
                </thead>'
        $.each(data, function (i, item) {
            $.each(data[i], function (j, obj) {

                badge_color = badge_color_from_state(obj.state);
                table_data += '<tr><td width="1%">' + obj.number + '</td>\
                <td width="10%">' + obj.created_by_user_name + '</td>\
                <td width="10%">' + obj.date_scheduled.split('.')[0] + '</td>\
                <td width="10%">' + obj.date_start.split('.')[0] + '</td>\
                <td width="10%">' + obj.date_done.split('.')[0] + '</td>\
                <td width="17%">' + obj.id + '</td>\
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
            autoWidth: false,
            "lengthMenu": [
                [15, 30, 100, -1],
                [15, 30, 100, "All"]
            ],
            "order": [
                [0, "desc"]
            ]
        })

        table.on('dblclick', 'tbody tr', function () {
            show_job(table.row(this).data()[5]);
        });

        $('.main-section').removeClass('hidden');
    });

}


function set_timeline_loglevel() {
    job_id = $('#job_id')[0].innerText
    $('.timeline li').remove()
    show_job(job_id, $('#log_severity')[0].value)
}


function update_timeline(job_id, table) {
    // client.jobs.read(job_id).done(function (data) {
    var state = $('#job_status').html()
    if ($('#job_id').length > 0) {
        if (state != "FAILURE" && state != "SUCCESS") {
            var current_serverity = $('#log_severity')[0].value
            var last_timestamp_rendered = $("#last_rendered_log_timestamp").text()
            var options = {}
            options["log-level"] = current_serverity
            if (last_timestamp_rendered) {
                options["logs-newer-than"] = last_timestamp_rendered;
            }
            // console.log(last_timestamp_rendered)

            client.jobs.read(job_id, {}, options).done(function (data) {
                render_logs(data)
                setTimeout(update_timeline, 2000, job_id, table);
            });


            // show_job(job_id,$('#log_severity')[0].value)

        }
    }
    // });

}


function download_file(url, filename) {
    access_token = sessionStorage.getItem('access_token');
    var req = new XMLHttpRequest();
    req.open("GET", url, true);
    req.setRequestHeader('Authorization', 'Bearer ' + access_token);
    req.responseType = "blob";
    req.onload = function (event) {
        event.preventDefault();
        var blob = req.response;

        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    };
    req.send();
}

function set_jinjamator_version() {
    access_token = sessionStorage.getItem('access_token');
    var req = new XMLHttpRequest();
    req.open("GET", "/api/info/version", true);
    req.setRequestHeader('Authorization', 'Bearer ' + access_token);
    req.onload = function (event) {
        event.preventDefault();
        var version_data = JSON.parse(req.response);
        console.log(version_data)
        $('.jinjamator_version').html("<b>Version</b> " + version_data.version)

    };
    req.send();
}



function render_logs(data) {
    $('#job_status').html(data['state']);
    $('#job_status').addClass("badge");
    $('#job_status').addClass(badge_color_from_state(data['state']));

    if (data.files.length > 0) {
        $("#job_files").html('');
        data['files'].forEach(function (value, index, array) {
            $('<a>', {
                text: value,
                title: value,
                href: '#',
            }).on('click', function () { download_file('/api/files/download/' + data.id + '/' + value, value) }).appendTo('#job_files');
            $('<br>').appendTo('#job_files');
        });
    }

    $.each(data['log'], function (index, log_item) {
        var timestamp = Object.keys(log_item)[0];
        var message = log_item[timestamp]['message']

        const json_regexp = /{.*\}/gm;

        var tasklet = log_item[timestamp]['current_tasklet']
        var serverity = log_item[timestamp]['level']




        $('#log_table').DataTable().row.add([timestamp, tasklet, serverity, log_item[timestamp]['configuration'],message]);

        // row_html = '<tr><td nowrap width="1%">' + timestamp +
        //     '</td><td nowrap width="1%" class="jinjamator_log_tasklet"><span class="tasklet_path_block">' + tasklet_short +
        //     '</span><span class="tasklet_path_none">' + tasklet +
        //     '</span></td><td width="1%"><span style="min-width:70px;" class="' + serverity_classes + '">' + serverity + '</span>\
        // </td><td><span class="jinjamator_log_message jinjamator_log_message_collapsed">' + message + '</span></td><td></td></tr>'
        // row_data = row_html


        // $('#log_table > tbody:last-child').append(row_html);

        // $('#log_table > tbody > tr:last-child > td:last-child').append(formatter.render())

        $("#last_rendered_log_timestamp").text(timestamp.replace(" ", "T"))


    })
    $('#log_table').DataTable().draw(false);

    // $('#log_table').DataTable({
    //     "lengthMenu": [
    //         [15, 30, 100, -1],
    //         [15, 30, 100, "All"]
    //     ]

    // }).draw();

    $('#log_table').on('click', '.jinjamator_log_message', function () {
        if ($(this).hasClass('jinjamator_log_message_raw')){
            $(this)[0].innerHTML=$(this)[0].innerHTML.replaceAll("\n","<BR>").replaceAll("\r","<BR>")
            $(this).removeClass('jinjamator_log_message_raw');
        }
        

        $(this).toggleClass('jinjamator_log_message_collapsed jinjamator_log_message_full');

    })

    $('#log_table').on('click', '.jinjamator_log_tasklet', function () {
        $(this).children().toggleClass('tasklet_path_block tasklet_path_none');

    })


}


function show_job(job_id, filter_serverity) {
    update_breadcrumb('Jobs', 'Detail');
    $.get("static/templates/main_content_section.html", function (data) {
        $(".all-content").html('<section class="content">' + data + '</section>');

        $.get("static/templates/timeline.html", function (data) {
            timeline_templates = $(data);
            var timeline = timeline_templates.filter('#timeline-template');
            var timeline_overview_box = timeline_templates.filter('#timeline-overview-box-template');
            timeline_overview_box.find('#job_id').html(job_id);

            // console.log("serv",filter_serverity)


            timeline.find('.timeline').append(timeline_overview_box.html());
            $(".all-content").html('<section class="content">' + timeline.html() + '</section>');

            if (filter_serverity) {

                $('#log_severity').val(filter_serverity);
            }

            var current_serverity = $('#log_severity')[0].value




            client.jobs.read(job_id, { "log-level": current_serverity }).done(function (data) {

                $("#user_name").html(data['created_by_user_name']);
                if ("debugger_password" in data) {
                    $("<tr> <th nowrap>Debugger URL:</th> \
                    <td nowrap id='debugger_url'>http://not-implemented-yet</td> \
                    <tr>").appendTo('#job_overview_table');
                }



                if ($.fn.dataTable.isDataTable('#log_table')) {
                    $('#log_table').DataTable().destroy();
                }

                table = $('#log_table').DataTable({
                    autoWidth: false,

                    // dom: 'Bfrtip',
                    // buttons: [
                    //     {
                    //         text: 'Create Role',
                    //         action: function (e, dt, node, config) {
                    //             create_role();
                    //         }
                    //     }
                    // ],
                    columns: [
                        {
                            title: 'Time',
                            className: "jinjamator_log_nowap_small",
                            width: '1%'
                        },
                        {
                            title: 'Tasklet',
                            className: "jinjamator_log_nowap_small jinjamator_log_tasklet",
                            width: '1%',
                            render: function (data, type, row) {
                                
                                var tasklet = data
                                var tasklet_short = tasklet
                                
                                if (tasklet.length > 15)
                                    var tasklet_short = "..." + tasklet.substring(tasklet.length - 12)

                                return '<span class="tasklet_path_block">' + tasklet_short + '</span><span class="tasklet_path_none">' + tasklet + '</span>'
                            }
                            
        
                        },
                        {
                            title: 'Level',
                            className: "jinjamator_log_nowap_small",
                            width: '1%',
                            render: function (data, type, row) {
                                serverity_classes = ""
                                switch (data) {
                                    case 'INFO':
                                        serverity_classes = 'badge bg-blue';
                                        break;
                                    case 'WARNING':
                                        serverity_classes = 'badge bg-yellow';
                                        break;
                                    case 'ERROR':
                                        serverity_classes = 'badge bg-red';
                                        break;
                                    case 'DEBUG':
                                        serverity_classes = 'badge bg-grey';
                                        break;
                                    case 'TASKLET_RESULT':
                                        serverity_classes = 'badge bg-green';
                                        break;
                                    case 'CONSOLE':
                                        serverity_classes = 'badge bg-black';
                                        break;
                                }
                                return '<span style="min-width:70px;" class="' + serverity_classes + '">' + data + '</span>'
                            }
                        },
                        {
                            title: 'Configuration',
                            className: 'jinjamator_log_nowap_small',
                            render: function (data, type, row, meta) {
                                
                                const formatter = new JSONFormatter(data, 0);
                                var div = document.createElement("div")
                                var icon = document.createElement("i")
                                icon.classList=["fa fa-fw fa-expand right jm_icon"]
                                
                                
                                var copy_raw=document.createElement("a")
                                copy_raw.setAttribute("href","#");
                                copy_raw.setAttribute("data-tooltip","Copied!")
                                


                                var copy_raw_icon = document.createElement("i")
                                copy_raw_icon.classList=["fa fa-fw fa-copy right jm_icon"]
                                copy_raw.appendChild(copy_raw_icon)
                                
                                
                                copy_raw.onclick = function(){
                                    navigator.clipboard.writeText(JSON.stringify(data,null, 2));
                                    $(this).toggleClass("show_tooltip")
                                      
                                    window.setTimeout(function(){$(this).toggleClass("show_tooltip")},2);
                                }
                                div.appendChild(copy_raw)
                                div.appendChild(icon)
                                icon.onclick = function() {
                                    if (formatter.open){
                                        formatter.openAtDepth(0);    
                                    }
                                    else{
                                        formatter.openAtDepth(1000);
                                    }
                                    
                                    icon.classList.toggle("fa-compress");
                                    icon.classList.toggle("fa-expand");
                                }

                                div.append(formatter.render())
                                return div                                            
                      
                      
                            }
                        },
                        {
                            title: 'Message',
                            render: function (data, type, row) {
                                var trimmed=data.trim()
                                if ((trimmed.startsWith("{") && trimmed.endsWith("}")) || (trimmed.startsWith("{") && trimmed.endsWith("}"))){
                                    try {
                                        var js_data=JSON.parse(trimmed)
                                        const formatter = new JSONFormatter(js_data, 0);
                                        formatter.openAtDepth(0);
                                        
                                        var div = document.createElement("div")
                                        
                                        var icon = document.createElement("i")
                                        icon.classList=["fa fa-fw fa-expand right jm_icon"]
                                
                                        var copy_raw = document.createElement("i")
                                        copy_raw.classList=["fa fa-fw fa-copy right jm_icon"]
                                        copy_raw.onclick = function(){
                                            try{
                                                navigator.clipboard.writeText(JSON.stringify(JSON.parse(data),null, 2));
                                            }
                                            catch(e){
                                                navigator.clipboard.writeText(data)  
                                            }
                                        }
                                        icon.onclick = function() {
                                            if (formatter.open){
                                                formatter.openAtDepth(0);    
                                            }
                                            else{
                                                formatter.openAtDepth(1000);
                                            }
                                            
                                            icon.classList.toggle("fa-compress");
                                            icon.classList.toggle("fa-expand");
                                        }
                                        
                                        div.append(copy_raw)
                                        div.append(formatter.render())
                                        return div
                                    }
                                    catch(e){ 
                                        try {
                                            // try to convert python datastructure to json -> this is a minimalistic poc, but works most of the time so it's good enough for now
                                            trimmed=trimmed.replaceAll("'","----'----")
                                            trimmed=trimmed.replaceAll('"',"'")
                                            trimmed=trimmed.replaceAll("----'----",'"')
                                            trimmed=trimmed.replaceAll(": None",': null')
                                            trimmed=trimmed.replaceAll(": True",': true')
                                            trimmed=trimmed.replaceAll(": False",': false')
                                            var js_data=JSON.parse(trimmed)
                                            const formatter = new JSONFormatter(js_data, 0);
                                            var div = document.createElement("div")
                                            var icon = document.createElement("i")
                                            icon.classList=["fa fa-fw fa-expand right jm_icon"]
                                
                                            var copy_raw = document.createElement("i")
                                            copy_raw.classList=["fa fa-fw fa-copy right jm_icon"]
                                            copy_raw.onclick = function(){
                                                try{
                                                    navigator.clipboard.writeText(JSON.stringify(JSON.parse(data),null, 2));
                                                }
                                                catch(e){
                                                    navigator.clipboard.writeText(data)  
                                                }
                                            }
                                            div.appendChild(icon)
                                            
                                            icon.onclick = function() {
                                                if (formatter.open){
                                                    formatter.openAtDepth(0);    
                                                }
                                                else{
                                                    formatter.openAtDepth(1000);
                                                }
                                                
                                                icon.classList.toggle("fa-compress");
                                                icon.classList.toggle("fa-expand");
                                            }
                                            
                                            div.append(formatter.render())
                                            return div                                            
                                  
                                            }
                                        catch(e){ 
                                        }
    
                                    }
                                }
                                var top_div = document.createElement("div")
                                top_div.style="display: inline-flex;box-sizing: border-box;min-width:100%;"
                                var l_div = document.createElement("div")
                                l_div.style="display: inline-block;min-width:100%;margin-right: -19px;"
                                var r_div = document.createElement("div")
                                r_div.style="float: right;box-sizing: border-box;"
                                var span = document.createElement("span")
                                span.classList=["jinjamator_log_message jinjamator_log_message_collapsed jinjamator_log_message_raw"]
                                
                                var copy_raw = document.createElement("i")
                                copy_raw.classList=["fa fa-fw fa-copy right jm_icon"]
                                copy_raw.onclick = function(){
                                    navigator.clipboard.writeText(data);
                                }
                                span.innerText=trimmed   
                                l_div.appendChild(span)
                                r_div.appendChild(copy_raw)
                                top_div.appendChild(l_div)
                                top_div.appendChild(r_div)
                                
                                return top_div
                            }
                            
                        },

                    ],
                    "lengthMenu": [
                        [15, 30, 100, -1],
                        [15, 30, 100, "All"]
                    ]

                })
                render_logs(data);
                $("#job_path").html(data['jinjamator_task']);





            });

            wizard_overlay.reset()
            $('.main-section').removeClass('hidden');

            setTimeout(update_timeline, 1000, job_id, table);


        });

    });


}