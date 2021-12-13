$(document).ready(function() {
    //temporary remove class extension
    (function($){

        $.fn.extend({ 
    
            temporaryRemoveClass: function(className, duration) {
                var elements = this;
                setTimeout(function() {
                    elements.addClass(className);
                }, duration);
    
                return this.each(function() {
                    $(this).removeClass(className);
                });
            }
        });
    
    })(jQuery);

    //confirm alert
    $('.confirm').click(function() {
        return window.confirm("Sind Sie sich sicher?");
    });

    //Delete a user on button click functionality
    $('.manage_employees .delete_button').click(function() {
        var employee_id = $(this).attr('employee_id')
        var ajaxReq = $.ajax({
                url: '/manage_users/'+employee_id,
                type: 'DELETE',
                statusCode: {
                    200: function() {
                        $("#deleteUserSucceeded").temporaryRemoveClass("hidden", 3000);
                        $(".manage_employees tr[employee_id=" + employee_id + "]").addClass("hidden");
                    },
                    500: function() {
                        $("#deleteUserFailed").temporaryRemoveClass("hidden", 3000);
                    }
                }
            });
    })

    //Edit a user
    $('.manage_employees .edit_button').click(function() {
        var employee_id = $(this).attr('employee_id')
        window.location = '/employee/' + employee_id
    })
});