window.BENCHMARK_DATA = {
  "lastUpdate": 1642379478303,
  "repoUrl": "https://github.com/RobertCraigie/prisma-client-py",
  "entries": {
    "prisma benchmark": [
      {
        "commit": {
          "author": {
            "name": "RobertCraigie",
            "username": "RobertCraigie"
          },
          "committer": {
            "name": "RobertCraigie",
            "username": "RobertCraigie"
          },
          "id": "d2fbcf54777e3589bb0cd42b17177efa76923f8a",
          "message": "feat(project): add benchmarks",
          "timestamp": "2022-01-16T02:29:50Z",
          "url": "https://github.com/RobertCraigie/prisma-client-py/pull/225/commits/d2fbcf54777e3589bb0cd42b17177efa76923f8a"
        },
        "date": 1642355626454,
        "tool": "pytest",
        "benches": [
          {
            "name": "test_prisma.py::test_create_scalars",
            "value": 43.74974895269012,
            "unit": "iter/sec",
            "range": "stddev: 0.03801571407709126",
            "extra": "mean: 22.85727401730636 msec\nrounds: 1329"
          },
          {
            "name": "test_prisma.py::test_create_with_relation",
            "value": 45.19236427630745,
            "unit": "iter/sec",
            "range": "stddev: 0.022470692703843956",
            "extra": "mean: 22.12763186909121 msec\nrounds: 2200"
          },
          {
            "name": "test_prisma.py::test_batched_create",
            "value": 17.214387122613683,
            "unit": "iter/sec",
            "range": "stddev: 0.02004807919445484",
            "extra": "mean: 58.0909440967753 msec\nrounds: 341"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "RobertCraigie",
            "username": "RobertCraigie"
          },
          "committer": {
            "name": "RobertCraigie",
            "username": "RobertCraigie"
          },
          "id": "d72a3eb908845d8faea1f53ee0320ec73aafae01",
          "message": "feat(project): add benchmarks",
          "timestamp": "2022-01-16T22:29:46Z",
          "url": "https://github.com/RobertCraigie/prisma-client-py/pull/225/commits/d72a3eb908845d8faea1f53ee0320ec73aafae01"
        },
        "date": 1642379477850,
        "tool": "pytest",
        "benches": [
          {
            "name": "test_queries.py::test_create_scalars",
            "value": 64.48838666056076,
            "unit": "iter/sec",
            "range": "stddev: 0.03455395321599365",
            "extra": "mean: 15.506667972073352 msec\nrounds: 1862"
          },
          {
            "name": "test_queries.py::test_create_with_relation",
            "value": 62.96595000789869,
            "unit": "iter/sec",
            "range": "stddev: 0.01929818581612668",
            "extra": "mean: 15.881599497419733 msec\nrounds: 3100"
          },
          {
            "name": "test_queries.py::test_batched_create",
            "value": 19.553353034338723,
            "unit": "iter/sec",
            "range": "stddev: 0.01991198656715321",
            "extra": "mean: 51.14212371882432 msec\nrounds: 409"
          }
        ]
      }
    ]
  }
}