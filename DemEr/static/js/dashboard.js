function getAlert(text, type) {
    return '<div class="alert alert-' + type +
        ' " role="alert">' + text + '</div>';
}

$(document).ready(function() {
    $('[data-toggle="popover"]').popover()
        .css('cursor', 'pointer');
    
    $('#patients table').dataTable({
        pageLength : 50,
        bLengthChange : false,
        language : {
            emptyTable : "No patients were found!"
        }
    });
    
    $('#doctors table').dataTable({
        pageLength : 50,
        bLengthChange : false,
        language : {
            emptyTable : "No doctors were found!"
        }
    })
    
    $('a').css('cursor', 'pointer');
    $('#doctors').hide();
    
    $('#toggle-view').click(function(e) {
        if ($(this).html() === 'View Doctors') {
            $(this).html('View Patients');
            $('#search').attr('placeholder', 'Search for a doctor.');
        }
        
        else {
            $(this).html('View Doctors');
            $('#search').attr('placeholder', 'Search for a patient.');
        }
        
        $('#doctors').toggle();
        $('#patients').toggle();
    });
    
    $('#search').on('input', function(e) {
        $('table:visible').DataTable().search(
            $('#search').val(),
            false,
            true
        ).draw();
    });
    
    $('.approve').click(function(e) {
        $(this).parent().children().hide();
        $(this).parent().children('.approve-confirm').show();
    });
    
    $('.reject').click(function(e) {
        $(this).parent().children().hide();
        $(this).parent().children('.reject-confirm').show();
    });
    
    $('.approve-no, .reject-no').click(function(e) {
        $(this).parent().parent().children().hide();
        $(this).parent().parent().children('.approve, .reject, .separator').show();
    });
    
    $('.remove').click(function(e) {
        $(this).parent().children().hide();
        $(this).parent().children('.remove-confirm').show();
    });
    
    $('.remove-no').click(function(e) {
        $(this).parent().parent().children().hide();
        $(this).parent().parent().children('.remove').show();
    });
    
    $('.approve-yes').click(function(e) {
        ID = $(this).attr('data-id');
        var elem = this;
        
        $.ajax({
            type : 'POST',
            dataType : 'json',
            contentType : 'application/json', 
            url : '/api/user/' + ID + '/approve',
            data : JSON.stringify({'accept' : true}),
            success : function(resp) {
                if (!resp.success) {
                    var stack_bottomright = {
                        'dir1' : 'up',
                        'dir2' : 'left'
                    };

                    new PNotify({ // yay notifications
                        title : 'Approval Error',
                        addclass : 'stack-bottomright',
                        stack : stack_bottomright,
                        text : resp.error,
                        delay : 2000,
                        type : 'error',
                        icon : false
                    });
                    
                    //return to original state
                    $(elem).siblings('.approve-no').click();
                    return false;
                }
                
                //change to a remove view
                var grand = $(elem).parent().parent()
                grand.html($('#remove-template').html())
                var docID = $(elem).attr('data-id');
                grand.find('.remove-yes').attr('data-id', docID);
            }
        });
    });
    
    $('.reject-yes, .remove-yes').click(function(e) {
        ID = $(this).attr('data-id');
        var elem = this;
        
        $.ajax({
            type : 'POST',
            dataType : 'json',
            contentType : 'application/json', 
            url : '/api/user/' + ID + '/approve',
            data : JSON.stringify({'accept' : false}),
            success : function(resp) {
                if (!resp.success) {
                    var stack_bottomright = {
                        'dir1' : 'up',
                        'dir2' : 'left'
                    };

                    new PNotify({ // yay notifications
                        title : 'Removal Error',
                        addclass : 'stack-bottomright',
                        stack : stack_bottomright,
                        text : resp.error,
                        delay : 2000,
                        type : 'error',
                        icon : false
                    });
                    
                    //return to original state
                    $(elem).siblings('.reject-no, .remove-no').click();
                    return false;
                }
                
                //change to a removed view
                var grand = $(elem).parent().parent()
                grand.html('Removed')
            }
        });
    });
});
