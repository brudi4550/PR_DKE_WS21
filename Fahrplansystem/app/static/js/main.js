$(document).ready(function() {
    //temporary remove class extension
    (function($){

        $.fn.extend({ 
    
            removeTemporaryClass: function(className, duration) {
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

    $('.manage_employees .delete_button').click(function() {
        var employee_id = $(this).attr('employee_id')
        var ajaxReq = $.ajax({
                url: '/manage_users/'+employee_id,
                type: 'DELETE',
                statusCode: {
                    200: function() {
                        $("#deleteUserSucceeded").removeTemporaryClass("hidden", 3000);
                        $(".manage_employees tr[employee_id=" + employee_id + "]").addClass("hidden");
                    },
                    500: function() {
                        $("#deleteUserFailed").removeTemporaryClass("hidden", 3000);
                    }
                }
            });
    })
});