var mode = 'none';

function getAlert(text, type) {
    return '<div class="alert alert-' + type +
        ' " role="alert">' + text + '</div>';
}

$(document).ready(function() {
    $('.forgot-button').click(function(e) {
        e.preventDefault();
        $(this).attr('disabled', true);
        
        //not the cleanest way to just get email?
        var creds = $('.login-form').serializeJSON();
        delete creds.password;
        
        Pace.track(function() {
            $.ajax({
                type : 'POST',
                dataType : 'json',
                contentType : 'application/json', 
                url : '/api/user/forgot',
                data : JSON.stringify(creds),
                success : function(resp) {
                    if (!resp.success) {
                        var stack_bottomright = {
                            'dir1' : 'up',
                            'dir2' : 'left'
                        };

                        new PNotify({ // yay notifications
                            title : 'Forgot Password',
                            addclass : 'stack-bottomright',
                            stack : stack_bottomright,
                            text : resp.error,
                            delay : 2000,
                            type : 'error',
                            icon : false
                        });
                        
                        $('.forgot-button').attr('disabled', false);
                        return false;
                    }
                    
                    var stack_bottomright = {
                        'dir1' : 'up',
                        'dir2' : 'left'
                    };

                    new PNotify({ // yay notifications
                        title : 'Forgot Password',
                        addclass : 'stack-bottomright',
                        stack : stack_bottomright,
                        text : resp.data,
                        delay : 2000,
                        type : 'success',
                        icon : false
                    });
                }
            });
        });
    });
    
    $('.login-button').click(function(e) {
        e.preventDefault(); //semi-AJAXy login
        var creds = $('.login-form').serializeJSON();
        $(this).attr('disabled', true);
        
        Pace.track(function() {
            $.ajax({
                type : 'POST',
                dataType : 'json',
                contentType : 'application/json', 
                url : '/api/login',
                data : JSON.stringify(creds),
                success : function(resp) {
                    if (!resp.success) {
                        var stack_bottomright = {
                            'dir1' : 'up',
                            'dir2' : 'left'
                        };

                        new PNotify({ // yay notifications
                            title : 'Login Error',
                            addclass : 'stack-bottomright',
                            stack : stack_bottomright,
                            text : resp.error,
                            delay : 2000,
                            type : 'error',
                            icon : false
                        });
                        
                        $('.login-button').attr('disabled', false);
                        return false;
                    }
                    
                    //resp.data contains redirect
                    window.location = resp.data;
                }
            });
        });
    });
    
    $('.signup-button').click(function(e) {
        mode = 'none';
        $('.signup-modal').modal('show');
        $('.signup-modal .alert').remove()
        $('.signup-form input').val('');
        $('.group-mode').addClass('hidden');
        $('.code-mode').addClass('hidden');
        $('.join-group').removeClass('hidden');
        $('.create-group').removeClass('hidden');
        $('.submit-signup').addClass('hidden')
           .prop('disabled', false);
    });
    
    $('.join-group').click(function(e) {
        mode = 'join';
        $('.group-mode').addClass('hidden');
        $('.code-mode').removeClass('hidden');
        $('.join-group').addClass('hidden');
        $('.create-group').removeClass('hidden');
        $('.submit-signup').removeClass('hidden');
    });
    
    $('.create-group').click(function(e) {
        mode = 'create';
        $('.code-mode').addClass('hidden');
        $('.group-mode').removeClass('hidden');
        $('.create-group').addClass('hidden');
        $('.join-group').removeClass('hidden');
        $('.submit-signup').removeClass('hidden');
    });
    
    $('#code').on('input', function(e) {
        if ($('#code').val() === '') {
            $('#code-name').val('');
            return false;
        }
        
        Pace.track(function() {
            $.ajax({
                type : 'GET',
                dataType : 'json',
                contentType : 'application/json', 
                url : '/api/clinic/' + $('#code').val(),
                success : function(resp) {
                    if (!resp.success) {
                        $('#code-name').val('');
                        return false;
                    }
                    
                    //resp.data contains clinic name
                    $('#code-name').val(resp.data);
                }
            });
        });
    });
    
    $('.submit-signup').click(function(e) {
        $(this).prop('disabled', true);
        var account = $('.signup-form').serializeJSON();
        
        if (mode === 'none') { 
            $(this).prop('disabled', false);
            return false;
        }
        
        if (account.password !== account.confirm) {
            $('.signup-modal .alert').remove()
            $('.signup-body').prepend(getAlert('Your confirmation does ' +
                'not match your password. Please try again.', 'danger')
            ); $(this).prop('disabled', false); return false;
        }
        
        if (mode === 'create') delete account.code;
        else if (mode === 'join') delete account.group;
        
        Pace.track(function() {
            $.ajax({
                type : 'POST',
                dataType : 'json',
                contentType : 'application/json', 
                url : '/api/user/create',
                data : JSON.stringify(account),
                success : function(resp) {
                    if (!resp.success) {
                        $('.signup-modal .alert').remove()
                        $('.signup-body').prepend(getAlert(resp.error, 'danger'));
                        $('.submit-signup').prop('disabled', false); return false;
                    }
                    
                    $('.signup-modal').modal('hide');
                    $('.success-modal').modal('show');
                }
            });
        });
    });
});
