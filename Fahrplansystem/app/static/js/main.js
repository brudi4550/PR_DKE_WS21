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

    //Delete a user on button click functionality
    $('.manage_employees .delete_button').click(function() {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
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
    });

    //Edit a user
    $('.manage_employees .edit_button').click(function() {
        var employee_id = $(this).attr('employee_id');
        window.location = '/employee/' + employee_id;
    });

    //show interval fields on choice repeat
    $('.repeat-tour-radio-buttons').click(function() {
        option = $('input[name=options]:checked', '#add-tour').val()
        if (option == 'repeat') {
            $('#interval-from').removeClass('hidden');
            $('#interval-to').removeClass('hidden');
            $('#interval').removeClass('hidden');
        } else {
            $('#interval-from').addClass('hidden');
            $('#interval-to').addClass('hidden');
            $('#interval').addClass('hidden');
            $('#interval-from').trigger('reset');
            $('#interval-to').trigger('reset');
            $('#interval').trigger('reset');
        }
    });
});