$(document).ready(function() {
    retrieve_data();
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
          url: "/stats_json?ticker=" + ticker,
          success: function(data){
              text_data = "Prices for "+data.ticker+" from "+data.start_date+" to "+data.end_date;
              $('#text_summary').html(text_data);
              text_data_2 = "Aggregating the returns in "+data.frequency+" day blocks and excluding the " + data.period_exclude + " top & bottom blocks of "+data.frequency+" day intervals."
              $('#text_summary_2').html(text_data_2);
              $('#ticker_start_value').html((data.ticker_start_value).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4 })+" "+data.fx);
              $('#ticker_end_value').html((data.ticker_end_value).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4 })+" "+data.fx);
              $('#period_tr').html((data.period_tr*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+" %");
              missed_txt = "on the top "+data.period_exclude+" blocks of "+data.frequency+" days";
              $('#missed').html(missed_txt);
              $('#nlargest_tr').html((data.nlargest_tr*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+" %");
              // $('#metamax').html((data.max).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%");
              // $('#metamin').html((data.min).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%");
              // lstmean = (data.lastvsmean).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })
              // crnt = "The last vol is "+lstmean+"% from the historical mean";
              // $('#metarel').html(crnt);
          }
  });

};
