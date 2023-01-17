// ajax call for register, if any error is occurred
//$('#register_btn').click(function() {
//debugger;
//    csr = $('input[name="csrfmiddlewaretoken"]').val();
//    register = $('#register_form').serializeArray();
//    username = register.at(1).value;
//    first_name = register.at(2).value;
//    last_name = register.at(3).value;
//    email = register.at(4).value;
//    password = register.at(5).value;
//    data = {'username': username, 'first_name': first_name, 'last_name': last_name,
//            'email': email, 'password': password, 'csrfmiddlewaretoken': csr}
//    $.ajax({
//    type: "POST",
//    url: "",
//    data: data,
//    dataType: 'json',
//    success: function(response) {
//            if (response.status === 'success'){
//                alertify.set('notifier', 'position', 'top-right');
//                alertify.success(response.message);
//            }
//            else {
//                for (let key in response.errors){
//                var error_msg = response.errors[key]
//                alertify.set('notifier', 'position', 'top-right');
//                alertify.error(error_msg.join(","));
////                window.location.href = response.redirect_url;
//                }
//            }
//    },
//    });
//});

// function for error message
function handleError() {
debugger;
    alertify.set('notifier', 'position', 'top-right');
    alertify.error("Please enter valid details to Register!!");
}


// function for daily log form error message
function validate() {
        user = document.forms['logForm']['user'].value;
        project = document.forms['logForm']['project'].value;
        date = document.forms['logForm']['date'].value;
        task = document.forms['logForm']['task'].value;
        description = document.forms['logForm']['description'].value;
        start_time = document.forms['logForm']['start_time'].value;
        end_time = document.forms['logForm']['end_time'].value;
        if (user || project || date || task || description || start_time || end_time == "") {
            alertify.set('notifier', 'position', 'top-right');
            alertify.error('All Fields are Required, Please check once!!');
        }
        return false;
}

function addTask(id) {
    if (id) {
        tr_id = '#user-'+id;
        $('#addTaskModal').modal('show');
        $('#form-user').val(id);
    }
    else { return false }
}

// function when you save the manually created log
function saveDailyLog() {
    csr = $('input[name="csrfmiddlewaretoken"]').val();
    user_id = parseInt($('#form-user').val());
    project_name = $('#form-project').val();
    date_id = $('#form-date').val();
    task_name = $('#task-name').val();
    description_id = $('#description-text').val();
    start_time_id = $('#start-time').val();
    end_time_id = $('#end-time').val();

    $.ajax({
        type: 'post',
        data: {'user': user_id, 'project_name': project_name, 'date': date_id, 'task': task_name,
        'description': description_id, 'start_time': start_time_id, 'end_time': end_time_id, 'csrfmiddlewaretoken': csr},
        url: '/add/log/',
        dataType: 'json',
        success: function(data){
                alertify.set('notifier', 'position', 'top-right');
                alertify.success('User Daily Log is created successfully!!');
                $('#addTaskModal').modal('hide');
        }
    })
}

// function for creating project by ajax call
function createProject(){
    csr = $('input[name="csrfmiddlewaretoken"]').val();
    project_name = $('#id_project').val();

    $.ajax({
        type: 'post',
        data: {'name': project_name, 'csrfmiddlewaretoken': csr},
        url: '/create/project/',
        dataType: 'json',
        success: function(data){
                alertify.set('notifier', 'position', 'top-right');
                alertify.success('Project is created successfully!!');
                $('#projectModal').modal('hide');
        }
    });

}

// function for creating task by ajax call
function createTask(){
    csr = $('input[name="csrfmiddlewaretoken"]').val();
    task_form = $('#task-form').serializeArray();
    project_name_val = parseInt(task_form.at(1).value);
    title = task_form.at(2).value;

    $.ajax({
        type: 'post',
        data: {'project': project_name_val, 'title': title, 'csrfmiddlewaretoken': csr},
        url: '/create/task/',
        dataType: 'json',
        success: function(data){
                alertify.set('notifier', 'position', 'top-right');
                alertify.success('Task is created successfully!!');
                $('#taskModal').modal('hide');
        }
    });

}

// for opening datetimepicker onclick of date field filter
$('#id_filter_date').datepicker({
    format:'yyyy-mm-dd',
    autoclose: true,
    useCurrent: false,
    widgetPositioning: {
        horizontal: 'auto',
        vertical: 'bottom'
    }
});

// clear all filter fields when you click on clear filter button
$('.clear-filter').click(function (){
    clearFilter();
});

function clearFilter(){
    // if any filter is applied then it will clear all filters and search query parameters
    // and reload the page
    window.location.href = window.location.href.split("?")[0];
}