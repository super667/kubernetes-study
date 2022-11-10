package histogram

import (
	"fmt"
	"github.com/prometheus/client_golang/prometheus"
)

var (
	TemperatureHistogram = prometheus.NewHistogram(prometheus.HistogramOpts{
		Name: "beijing_temperature",
		Help: "The temperature of the beijing",
		Buckets: prometheus.LinearBuckets(0,10,3),
	})
)

