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

    //Delete a user on button click
    $('.manage_employees .delete_button').click(function() {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var employee_id = $(this).attr('employee_id')
        var ajaxReq = $.ajax({
                url: '/manage_employees/'+employee_id,
                type: 'DELETE',
                statusCode: {
                    200: function() {
                        window.location.reload()
                    },
                    500: function() {
                        $("#deleteEmployeeFailed").temporaryRemoveClass("hidden", 3000);
                    }
                }
            });
    });

    //Delete tour on button click
    $('.manage_tours .delete_button').click(function() {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var tour_id = $(this).attr('tour_id')
        var ajaxReq = $.ajax({
                url: '/manage_tours/'+tour_id,
                type: 'DELETE',
                statusCode: {
                    200: function() {
                        window.location.reload()
                    },
                    500: function() {
                        $("#deleteTourFailed").temporaryRemoveClass("hidden", 3000);
                    }
                }
            });
    });

    // Delete crew on button click
    $('.manage_crews .delete_button').click(function() {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var tour_id = $(this).attr('crew_id')
        var ajaxReq = $.ajax({
                url: '/manage_crews/'+tour_id,
                type: 'DELETE',
                statusCode: {
                    200: function() {
                        window.location.reload()
                    },
                    500: function() {
                        $("#deleteCrewFailed").temporaryRemoveClass("hidden", 3000);
                    }
                }
            });
    });

    //Edit a user
    $('.manage_employees .edit_button').click(function() {
        var employee_id = $(this).attr('employee_id');
        window.location = '/employee/' + employee_id;
    });

    //Edit a tour
    $('.manage_tours .edit_button').click(function() {
        var tour_id = $(this).attr('tour_id');
        window.location = '/tour/' + tour_id;
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
        }
    });

    // Add empty crew
    $('.manage_crews .add_empty_crew').click(function() {
        var ajaxReq = $.ajax({
                url: '/add_empty_crew',
                type: 'POST'
            });
        window.location.reload()
    });

});