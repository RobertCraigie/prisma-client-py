from __future__ import annotations

from typing import Generic, List, Tuple, TypeVar, Dict, NamedTuple

from pydantic import BaseModel
from pydantic.generics import GenericModel


__all__ = (
    'Metrics',
    'Metric',
    'MetricHistogram',
)


_T = TypeVar('_T')


class Metrics(BaseModel):
    counters: List[Metric[int]]
    gauges: List[Metric[float]]
    histograms: List[Metric[MetricHistogram]]


class Metric(GenericModel, Generic[_T]):
    key: str
    value: _T
    labels: Dict[str, str]
    description: str


class MetricHistogram(BaseModel):
    sum: float
    count: int
    buckets: List[HistogramBucket]


class HistogramBucket(NamedTuple):
    max_value: float
    total_count: int


Metric.update_forward_refs()
Metrics.update_forward_refs()
MetricHistogram.update_forward_refs()
