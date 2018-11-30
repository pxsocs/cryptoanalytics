$(document).ready(function() {
    $body = $("body");

    $(document).on({
        ajaxStart: function() {$body.addClass("loading");},
        ajaxStop: function() {$body.removeClass("loading");}
    });

    retrieve_data();
    $('.monitor_chg').on('change', retrieve_data);
} );

function retrieve_data() {
    var ticker = $('#ticker').val()
    var start_date = $('#start_date').val()
    var end_date = $('#end_date').val()
    var frequency = $('#frequency').val()
    var period_exclude = $('#period_exclude').val()
    var fx = $('#fx').val()

    $.ajax({
          type: "GET",
          dataType: 'json',
          url: "/stats_json?ticker="+ticker+"&force=False&fx="+fx+"&start_date="+start_date+"&end_date="+end_date+"&frequency="+frequency+"&period_exclude="+period_exclude,
          success: function(data){
              if (data.status == "error") {
                   clean_data();
                   $('#error_message').html("Something went wrong when requesting data. Is that a valid ticker?");
              } else {
              $('#error_message').html(" ");
              text_data = "Requested prices for "+data.ticker+" from "+data.start_date+" to "+data.end_date;
              $('#text_summary').html(text_data);
              text_data_0 = "Range of available data: from "+data.set_initial_time+" to "+data.set_final_time
              $('#text_summary_0').html(text_data_0);
              text_data_2 = "Aggregating the returns in "+data.frequency+" day blocks and excluding the " + data.period_exclude + " top blocks of "+data.frequency+" day intervals."
              $('#text_summary_2').html(text_data_2);
              $('#ticker_start_value').html((data.ticker_start_value).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4 })+" "+data.fx);
              $('#ticker_end_value').html((data.ticker_end_value).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4 })+" "+data.fx);
              $('#period_tr').html((data.period_tr*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+" %");
              missed_txt = "on the top "+data.period_exclude+" periods of "+data.frequency+" days";
              $('#missed').html(missed_txt);
              $('#nlargest_tr').html((data.nlargest_tr*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+" %");
              $('#exclude_nlargest_tr').html((data.exclude_nlargest_tr*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+" %");
              difference = (data.exclude_nlargest_tr - data.period_tr)
              $('#difference').html((difference*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+" %");
              $('#n_largest').html(data.nlargest);
              var start_date = new Date(data.start_date);
              var end_date = new Date(data.end_date);
              var n_days = new Date(end_date - start_date);
              n_days = n_days/1000/60/60/24;
              var missed_days = (data.frequency * data.period_exclude);
              var pct_missed = (missed_days / n_days) * 100;
              var return_missed = (data.nlargest_tr / data.period_tr) * 100

              n_days = n_days.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0 });
              missed_days = missed_days.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0 });
              pct_missed = pct_missed.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 });
              return_missed = return_missed.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 });

              returns_msg = "Out of a total of "+n_days+" days, you would have missed "+missed_days+" days or "+pct_missed+"% of the time."
              $('#returns_msg').html(returns_msg);

              missed_msg = "By not being allocated "+pct_missed+"% of the time, you would have missed "+return_missed+"% of the returns during this period"
              $('#missed_msg').html(missed_msg);

              }
          }
  });

};

function clean_data() {

    $('#text_summary').html(" ");
    $('#text_summary_0').html(" ");
    $('#text_summary_2').html(" ");
    $('#ticker_start_value').html("-");
    $('#ticker_end_value').html("-");
    $('#period_tr').html("-");
    $('#missed').html("-");
    $('#nlargest_tr').html("-");
    $('#exclude_nlargest_tr').html("-");
    $('#difference').html("-");
    $('#n_largest').html("-");
    $('#returns_msg').html(" ");
    $('#missed_msg').html(" ");
};
