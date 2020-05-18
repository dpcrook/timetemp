---
title: "Hourly Temperature and Pressure"
categories:
  - Chart
tags:
  - phant
last_modified_at: 2020-05-18T02:59:24Z
---

{% include temp_pres_charts.html %}

<script>
var drawThisChart = creata_drawChart('?gt[timestamp]=now%20-24%20hours', 'chart-hourly');
google.charts.setOnLoadCallback(drawThisChart);
</script>

<div id="chart-hourly" style="width: 100%;"></div>
<div id="save_png"></div>


<!-- Local Variables: -->
<!-- time-stamp-pattern: "8/^last_modified_at: %:y-%02m-%02dT%02H:%02M:%02SZ$" -->
<!-- time-stamp-time-zone: "UTC" -->
<!-- End: -->
