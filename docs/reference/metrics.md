# Metrics

Prisma Metrics gives you detailed insight into how Prisma is interactting with your Database. For more detailed information see the [Prisma Documentation](https://www.prisma.io/docs/concepts/components/prisma-client/metrics).

To access metrics in the Python client

Metrics can be accessed in the Python client through the `Prisma.get_metrics()` method. Two different formats are available, `json` and `prometheus`.

## JSON Format

The default format is `json` which returns a `prisma.Metrics` instance:

```py
from prisma import Prisma

client = Prisma()

metrics = client.get_metrics()
print(metrics.counters[0])
```

See the [Prisma Documentation](https://www.prisma.io/docs/concepts/components/prisma-client/metrics#retrieve-metrics-in-json-format) for more details on the structure of the metrics object.

## Prometheus Format

The `prometheus` format returns a `str` which is a valid [Prometheus data](https://prometheus.io/).


```py
from prisma import Prisma

client = Prisma()

metrics = client.get_metrics(format='prometheus')
print(metrics)
```

See the [Prisma Documentation](https://www.prisma.io/docs/concepts/components/prisma-client/metrics#retrieve-metrics-in-prometheus-format) for more details on the structure of the data.
