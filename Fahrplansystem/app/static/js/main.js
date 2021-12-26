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
    $('.delete_employee').click(function() {
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

    // Delete crew on button click
    $('.delete_crew').click(function() {
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

    //Delete tour on button click
    $('.delete_tour').click(function() {
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

     $('.delete_trip').click(function() {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var trip_id = $(this).attr('trip_id')
        var ajaxReq = $.ajax({
            url: '/manage_trips/'+ trip_id,
            type: 'DELETE',
            statusCode: {
                200: function() {
                    window.location.reload()
                },
                500: function() {
                    $("#deleteTripFailed").temporaryRemoveClass("hidden", 3000);
                }
            }
        });
    });

    $('.delete_rushhour').click(function() {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var rushhour_id = $(this).attr('rushhour_id')
        var ajaxReq = $.ajax({
            url: '/delete_rushhour/'+ rushhour_id,
            type: 'DELETE',
            statusCode: {
                200: function() {
                    window.location.reload()
                },
                500: function() {
                    $("#deleteTripFailed").temporaryRemoveClass("hidden", 3000);
                }
            }
        });
    });

});