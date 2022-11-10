package main

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"test_histograms/src/histogram"
	"test_histograms/src/summary"

	"log"
	"net/http"
)

func init()  {
	prometheus.MustRegister(histogram.TemperatureHistogram)
	prometheus.MustRegister(summary.SalarySummary)
}

func main()  {
		histogram.InsertTemperature()
		summary.InsertSummary()
		http.Handle("/metrics", promhttp.Handler())
		log.Fatal(http.ListenAndServe(":8080",nil))
}
