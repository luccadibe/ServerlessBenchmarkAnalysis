# Intermediate Results

## Coldstarts

![Coldstart CDF Node](cdf_Node.js.png)

![Coldstart CDF Python](cdf_Python.png)

![Coldstart CDF Golang](cdf_Golang.png)

![Coldstarts Boxplot](coldstarts-boxplot.png)

## RampUp

![RampUp Median Latency](rampup_50.png)

![RampUp Tail Latency](rampup_99.png)

## GeoDis

### Generalised

![GeoDis generalised results](geodis-ecdf.png)

### Load Zone Group 1

![GeoDis1 results](geodis1-bar.png)
![GeoDis1 results](geodis1-box.png)

### Load Zone Group 2

![GeoDis2 results](geodis2-bar.png)
![GeoDis2 results](geodis2-box.png)

## Inline Data Transfer

Currently, there are practically no results for Flyio for this test because of a bug in the test script. Internal http requests in flyio apps can only be done with warm instances. Thus, we needed to "wake up" the consumer instance each time.

![Inline Data boxplot](inline_latency_boxplot.png)
