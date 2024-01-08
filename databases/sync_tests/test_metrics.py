from prisma import Prisma
from prisma._compat import model_json


def test_prometheus(client: Prisma) -> None:
    """Metrics can be returned in Prometheus format"""
    client.user.create(data={'name': 'Robert'})

    metrics = client.get_metrics(format='prometheus')

    assert 'prisma_client_queries_total' in metrics
    assert 'prisma_datasource_queries_total' in metrics
    assert 'prisma_client_queries_active' in metrics
    assert 'prisma_client_queries_duration_histogram_ms_bucket' in metrics


def test_json_string(client: Prisma) -> None:
    """Metrics can be serlialized to JSON"""
    client.user.create(data={'name': 'Robert'})

    metrics = client.get_metrics()
    assert isinstance(model_json(metrics), str)


def test_json(client: Prisma) -> None:
    """Metrics returned in the JSON format"""
    client.user.create(data={'name': 'Robert'})

    metrics = client.get_metrics(format='json')

    assert len(metrics.counters) > 0
    assert metrics.counters[0].value > 0

    assert len(metrics.gauges) > 0
    gauge = next(filter(lambda g: g.key == 'prisma_pool_connections_open', metrics.gauges))
    assert gauge.value > 0

    assert len(metrics.histograms) > 0
    assert metrics.histograms[0].value.sum > 0
    assert metrics.histograms[0].value.count > 0

    assert len(metrics.histograms[0].value.buckets) > 0

    for bucket in metrics.histograms[0].value.buckets:
        assert bucket.max_value >= 0
        assert bucket.total_count >= 0


def test_global_labels(client: Prisma) -> None:
    metrics = client.get_metrics(global_labels={'foo': 'bar'})
    assert metrics.counters[0].labels == {'foo': 'bar'}
