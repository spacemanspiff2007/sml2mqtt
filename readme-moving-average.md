# sml2mqtt moving average

This patch adds a moving average transformation to  sml2mqtt to support averaging a value over a moving buffer.

- https://en.wikipedia.org/wiki/Moving_average

The MovingAverage transformation is activated using the `moving_avg` keyword that provides the size of the buffer.

```
    values:
        0100010800ff:
          mqtt:
            topic: Total_in
          filters:
            - every: 10
            - diff: 1000000
        0100100700ff:
          mqtt:
            topic: Power_curr
          filters:
            - every: 10
            - diff: 1000000
          transformations:
            - moving_avg: 10
            - round: 0
```

Log level of DEBUG provides insights into how the buffer is getting built up and managed


```
[2023-06-17 13:49:03,124] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.__init__(10)
[2023-06-17 13:49:03,124] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1814.359 -> [1814.359] -> 1814.359
[2023-06-17 13:49:03,125] [sml.ttyUSB0.status     ] INFO     | OK
[2023-06-17 13:49:03,323] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1823.03 -> [1814.359, 1823.03] -> 1818.6945
[2023-06-17 13:49:03,810] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1820.332 -> [1814.359, 1823.03, 1820.332] -> 1819.2403333333334
[2023-06-17 13:49:04,012] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1776.966 -> [1814.359, 1823.03, 1820.332, 1776.966] -> 1808.67175
[2023-06-17 13:49:04,212] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1739.612 -> [1814.359, 1823.03, 1820.332, 1776.966, 1739.612] -> 1794.8597999999997
[2023-06-17 13:49:04,810] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1745.11 -> [1814.359, 1823.03, 1820.332, 1776.966, 1739.612, 1745.11] -> 1786.5681666666667
[2023-06-17 13:49:05,012] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1738.151 -> [1814.359, 1823.03, 1820.332, 1776.966, 1739.612, 1745.11, 1738.151] -> 1779.6514285714286
[2023-06-17 13:49:05,211] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1738.852 -> [1814.359, 1823.03, 1820.332, 1776.966, 1739.612, 1745.11, 1738.151, 1738.852] -> 1774.5515
[2023-06-17 13:49:05,810] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1730.52 -> [1814.359, 1823.03, 1820.332, 1776.966, 1739.612, 1745.11, 1738.151, 1738.852, 1730.52] -> 1769.659111111111
[2023-06-17 13:49:06,012] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1752.945 -> [1814.359, 1823.03, 1820.332, 1776.966, 1739.612, 1745.11, 1738.151, 1738.852, 1730.52, 1752.945] -> 1767.9877000000001
[2023-06-17 13:49:06,213] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1738.287 -> [1823.03, 1820.332, 1776.966, 1739.612, 1745.11, 1738.151, 1738.852, 1730.52, 1752.945, 1738.287] -> 1760.3805
[2023-06-17 13:49:06,810] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1746.341 -> [1820.332, 1776.966, 1739.612, 1745.11, 1738.151, 1738.852, 1730.52, 1752.945, 1738.287, 1746.341] -> 1752.7116
[2023-06-17 13:49:07,012] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1750.677 -> [1776.966, 1739.612, 1745.11, 1738.151, 1738.852, 1730.52, 1752.945, 1738.287, 1746.341, 1750.677] -> 1745.7461000000003
[2023-06-17 13:49:07,213] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1739.682 -> [1739.612, 1745.11, 1738.151, 1738.852, 1730.52, 1752.945, 1738.287, 1746.341, 1750.677, 1739.682] -> 1742.0176999999999
[2023-06-17 13:49:07,809] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1746.324 -> [1745.11, 1738.151, 1738.852, 1730.52, 1752.945, 1738.287, 1746.341, 1750.677, 1739.682, 1746.324] -> 1742.6888999999999
[2023-06-17 13:49:08,010] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1745.787 -> [1738.151, 1738.852, 1730.52, 1752.945, 1738.287, 1746.341, 1750.677, 1739.682, 1746.324, 1745.787] -> 1742.7566
[2023-06-17 13:49:08,211] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1744.516 -> [1738.852, 1730.52, 1752.945, 1738.287, 1746.341, 1750.677, 1739.682, 1746.324, 1745.787, 1744.516] -> 1743.3931
[2023-06-17 13:49:08,810] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1745.534 -> [1730.52, 1752.945, 1738.287, 1746.341, 1750.677, 1739.682, 1746.324, 1745.787, 1744.516, 1745.534] -> 1744.0613
[2023-06-17 13:49:09,012] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1750.82 -> [1752.945, 1738.287, 1746.341, 1750.677, 1739.682, 1746.324, 1745.787, 1744.516, 1745.534, 1750.82] -> 1746.0913
[2023-06-17 13:49:09,213] [sml.mqtt               ] DEBUG    | MovingAverageTransformation.process(1629.693 -> [1738.287, 1746.341, 1750.677, 1739.682, 1746.324, 1745.787, 1744.516
```

