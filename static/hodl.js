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
          url: "/stats_json?ticker="+ticker+"&force=True&fx="+fx+"&start_date="+start_date+"&end_date="+end_date+"&frequency="+frequency+"&period_exclude="+period_exclude,
          success: function(data){
              text_data = "Downloaded Prices for "+data.ticker+" from "+data.set_initial_time+" to "+data.set_final_time;
              $('#text_summary').html(text_data);
              text_data_2 = "Aggregating the returns in "+data.frequency+" day blocks and excluding the " + data.period_exclude + " top blocks of "+data.frequency+" day intervals."
              $('#text_summary_2').html(text_data_2);
              $('#ticker_start_value').html((data.ticker_start_value).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4 })+" "+data.fx);
              $('#ticker_end_value').html((data.ticker_end_value).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4 })+" "+data.fx);
              $('#period_tr').html((data.period_tr*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+" %");
              missed_txt = "on the top "+data.period_exclude+" blocks of "+data.frequency+" days";
              $('#missed').html(missed_txt);
              $('#nlargest_tr').html((data.nlargest_tr*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+" %");
              $('#exclude_nlargest_tr').html((data.exclude_nlargest_tr*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+" %");
              difference = (data.exclude_nlargest_tr - data.period_tr)
              $('#difference').html((difference*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+" %");
              console.log(data.nlargest)
              $('#n_largest').html(data.nlargest);
          }
  });

};
