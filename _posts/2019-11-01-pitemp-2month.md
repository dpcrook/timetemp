---
title: "Sixty-day rpif1 Temperature"
categories:
  - Chart
tags:
  - phant
last_modified_at: 2019-11-11T05:46:44Z
---

{% include pi_temp_charts.html %}

<script>
var drawThisChart = creata_drawChart('?gt[timestamp]=now%20-61%20days&sample=36', 'chart-bimonthly');
google.charts.setOnLoadCallback(drawThisChart);
</script>

<div id="chart-bimonthly" style="width: 100%;"></div>
<div id="save_png"></div>


<!-- Local Variables: -->
<!-- time-stamp-pattern: "8/^last_modified_at: %:y-%02m-%02dT%02H:%02M:%02SZ$" -->
<!-- time-stamp-time-zone: "UTC" -->
<!-- End: -->
