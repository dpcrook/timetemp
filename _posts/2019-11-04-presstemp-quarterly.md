---
title: "Quarterly Temperature and Pressure"
categories:
  - Chart
tags:
  - phant
last_modified_at: 2020-05-18T03:00:03Z
---

{% include temp_pres_charts.html %}

<script>
var drawThisChart = creata_drawChart('?gt[timestamp]=now%20-91%20days&sample=18', 'chart-quarterly');
google.charts.setOnLoadCallback(drawThisChart);
</script>

<div id="chart-quarterly" style="width: 100%;"></div>
<div id="save_png"></div>

<!-- Local Variables: -->
<!-- time-stamp-pattern: "8/^last_modified_at: %:y-%02m-%02dT%02H:%02M:%02SZ$" -->
<!-- time-stamp-time-zone: "UTC" -->
<!-- End: -->
