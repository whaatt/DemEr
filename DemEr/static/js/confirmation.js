var mode = 'none';

function getAlert(text, type) {
    return '<div class="alert alert-' + type +
        ' " role="alert">' + text + '</div>';
}

$(document).ready(function() {
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
});
