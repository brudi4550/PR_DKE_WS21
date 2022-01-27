//jquery functions
$(document).ready(function () {
    //temporary remove class extension
    (function ($) {
        $.fn.extend({
            temporaryRemoveClass: function (className, duration) {
                var elements = this;
                setTimeout(function () {
                    elements.addClass(className);
                }, duration);

                return this.each(function () {
                    $(this).removeClass(className);
                });
            }
        });
    })(jQuery);

    //Delete a user on button click
    $('.delete_employee').click(function () {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var employee_id = $(this).attr('employee_id')
        var ajaxReq = $.ajax({
            url: '/manage_employees/' + employee_id,
            type: 'DELETE',
            statusCode: {
                200: function () {
                    window.location.reload()
                },
                500: function () {
                    $("#deleteEmployeeFailed").temporaryRemoveClass("hidden", 3000);
                }
            }
        });
    });

    // Delete crew on button click
    $('.delete_crew').click(function () {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var tour_id = $(this).attr('crew_id')
        var ajaxReq = $.ajax({
            url: '/manage_crews/' + tour_id,
            type: 'DELETE',
            statusCode: {
                200: function () {
                    window.location.reload()
                },
                500: function () {
                    $("#deleteCrewFailed").temporaryRemoveClass("hidden", 3000);
                }
            }
        });
    });

    //Delete tour on button click
    $('.delete_tour').click(function () {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var tour_id = $(this).attr('tour_id')
        var ajaxReq = $.ajax({
            url: '/manage_tours/' + tour_id,
            type: 'DELETE',
            statusCode: {
                200: function () {
                    window.location.reload()
                },
                500: function () {
                    $("#deleteTourFailed").temporaryRemoveClass("hidden", 3000);
                }
            }
        });
    });

    //Delete trip on button click
    $('.delete_trip').click(function () {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var trip_id = $(this).attr('trip_id')
        var ajaxReq = $.ajax({
            url: '/manage_trips/' + trip_id,
            type: 'DELETE',
            statusCode: {
                200: function () {
                    window.location.reload()
                },
                500: function () {
                    $("#deleteTripFailed").temporaryRemoveClass("hidden", 3000);
                }
            }
        });
    });

    //Delete rushhour on button click
    $('.delete_rushhour').click(function () {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var rushhour_id = $(this).attr('rushhour_id')
        var ajaxReq = $.ajax({
            url: '/delete_rushhour/' + rushhour_id,
            type: 'DELETE',
            statusCode: {
                200: function () {
                    window.location.reload()
                },
                500: function () {
                    $("#deleteTripFailed").temporaryRemoveClass("hidden", 3000);
                }
            }
        });
    });

    //Delete interval on button click
    $('.delete_interval').click(function () {
        if (!window.confirm("Sind Sie sich sicher?")) {
            return
        }
        var interval_id = $(this).attr('interval_id')
        var ajaxReq = $.ajax({
            url: '/manage_interval/' + interval_id,
            type: 'DELETE',
            statusCode: {
                200: function () {
                    window.location.reload()
                },
                500: function () {
                    $("#deleteTripFailed").temporaryRemoveClass("hidden", 3000);
                }
            }
        });
    });

    //Send timetable update patch request on button click
    $('.update-timetable').click(function () {
        var ajaxReq = $.ajax({
            url: '/local_update_timetable',
            type: 'PATCH',
            statusCode: {
                200: function () {
                    window.location.reload()
                }
            }
        });
    });

    //admin homepage timer for all tours
    $('.tour-timer').each(function (i, obj) {
        var timer = $(this);
        var secs = timer.attr('until');
        secs = parseInt(secs);
        setInterval(function () {
            var days = Math.floor(secs / 84600);
            var days_remainder = secs % 84600;
            var hours = Math.floor(days_remainder / 3600);
            var hours_remainder = days_remainder % 3600;
            var minutes = Math.floor(hours_remainder / 60);
            var seconds = hours_remainder % 60;
            timer.text(seconds + ' Sekunden')
            if (days != 0) {
                timer.prepend(days + ' Tage ' + hours + ' Stunden ' + minutes + ' Minuten ')
            } else if (hours != 0) {
                timer.prepend(hours + ' Stunden ' + minutes + ' Minuten ')
            } else if (minutes != 0) {
                timer.prepend(minutes + ' Minuten ')
            }
            if (secs > 0) {
                secs--;
            }
        }, 1000);
    });

});

//non jquery functions
//set image when start dragging employee
function drag_employee(ev) {
    ev.dataTransfer.setData('data', ev.target.getAttribute('employee_id'));
    let img = document.createElement('img');
    img.src = '/static/images/employee.png';
    ev.dataTransfer.setDragImage(img, 25, 25);
}

//send request when employee is dropped on a crew
function drop_employee(ev) {
    ev.preventDefault();
    var crew_id = ev.target.getAttribute('crew_id');
    var data = ev.dataTransfer.getData('data');
    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/move_employee_to_crew', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        employee_id: data,
        crew_id: crew_id
    }));
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            window.location.reload();
        }
    }
}

function allowDrop(ev) {
    ev.preventDefault();
}