---
permalink: /about/
title: "About"
---

## This Site

This is hosted in a Jekyll / Github Pages [`gh-pages` branch](https://github.com/idcrook/timetemp/tree/gh-pages).

On this site, the charts are generated locally on your browser with Google's  [Google Charts](https://developers.google.com/chart/interactive/docs) JavaScript charting library.


## TimeTemp logger (Temperature and Pressure)

 - Blog post
   - [Migrating to phant and updated Adafruit libraries](https://idcrook.github.io/Moving-Indoor-Weather-Logging-To-Phant/)
   - No blog post, but in June 2018, updated to [python3 libraries](https://github.com/idcrook/timetemp/blob/master/install/BUILD_PYTHON3.md)
 - GitHub Project
   - [Source and Docs](https://github.com/idcrook/timetemp) (GitHub repository)
   - [https://idcrook.github.io/timetemp](https://idcrook.github.io/timetemp) (what you are reading now)

## Pitemp logger (Raspberry Pi Model 4 B Temperature)

 - Also phant logger based
 - The Pi 4 serves as a kubernetes worker node.
   - has always had a heatsink
   - has a good (3d printed) case with fan
     - drops about 15°C: from 70C -> 55C
   - the bigger systematic impact seems to be the eeprom update for the USB
     - drops another 25°C: 55C -> 30C

![rpif1 sixty day temperature log](/assets/images/sixty_day_rpif1_temp.png)

 - GitHub Project
   - [Source and Docs](https://github.com/idcrook/pitempmon) (GitHub repository)
