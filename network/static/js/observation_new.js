$(function () {
    $('#datetimepicker-start').datetimepicker();
    $('#datetimepicker-start').data('DateTimePicker').setMinDate(moment().add(1,'h'));
    $('#datetimepicker-end').datetimepicker();
    $("#datetimepicker-start").on('dp.change',function (e) {
        //Setting minimum and maximum for end
        $('#datetimepicker-end').data('DateTimePicker').setMinDate(e.date);
        $('#datetimepicker-end').data('DateTimePicker').setMaxDate(moment(e.date).add(24, 'h'));
    });

    $('#satellite-selection').change( function() {
        var norad = $(this).find(':selected').data('norad');
        $('#transponder-selection').prop('disabled', false);
        $('#transponder-selection option').hide();
        $('#transponder-selection option[data-satellite="'+norad+'"]').show().prop('selected', true);
        if($('#transponder-selection option:visible').length === 0) {
            $('#transponder-selection').prop('disabled', true);
            $('#transponder-selection option[id="no-transponder"]').show().prop('selected', true);
        }
    });
});

$( document ).ready( function(){
    $('#calculate-observation').click( function(){
        $('.calculation-result').show();
        var satellite = $('#satellite-selection').val();
        var start_time = $('#datetimepicker-start input').val();
        var end_time = $('#datetimepicker-end input').val();

        $.ajax({
            url: '/prediction_windows/' + satellite + '/' + start_time + '/' + end_time + '/'
        }).done(function(data) {
            var dc = 0; //Data counter
            var suggested_data = [];
            $.each(data, function( i,k ){
                label = k.id + ' - ' + k.name;
                var times = [];
                $.each(k.window, function( m,n ){
                    var starting_time = moment(n.start).valueOf();
                    var ending_time = moment(n.end).valueOf();
                    $('#windows-data').append('<input type="hidden" name="'+dc+'-starting_time" value="'+n.start+'">');
                    $('#windows-data').append('<input type="hidden" name="'+dc+'-ending_time" value="'+n.end+'">');
                    $('#windows-data').append('<input type="hidden" name="'+dc+'-station" value="'+k.id+'">');
                    times.push({starting_time: starting_time, ending_time: ending_time})
                    dc = dc +1;
                });
                suggested_data.push({label : label, times : times});
            });

            $('#windows-data').append('<input type="hidden" name="total" value="'+dc+'">');
            timeline_init(start_time, end_time, suggested_data);
        });
    });
});

function timeline_init( start, end, payload ){
    var start_time_timeline = moment(start).valueOf();
    var end_time_timeline = moment(end).valueOf();

    $('#timeline').empty();

    var chart = d3.timeline()
                  .stack()
                  .beginning(start_time_timeline)
                  .ending(end_time_timeline)
                  .hover(function (d, i, datum) {
                      var div = $('#hoverRes');
                      var colors = chart.colors();
                      div.find('.coloredDiv').css('background-color', colors(i))
                      div.find('#name').text(datum.label);
                  })
                  .margin({left:140, right:10, top:0, bottom:50})
                  .tickFormat({format: d3.time.format('%H:%M'), tickTime: d3.time.minutes, tickInterval: 30, tickSize: 6});

    var svg = d3.select('#timeline').append('svg').attr('width', 1140)
                .datum(payload).call(chart);
}
