import asyncio
import time

import pytest


@pytest.mark.benchmark(group="clip_create")
def test_clip_creation_speed(benchmark):
    # Lightweight synthetic benchmark to establish baseline for clip creation path.
    async def create_op():
        # Simulate small work similar to ClipService.create_clip
        await asyncio.sleep(0)

    def run():
        asyncio.get_event_loop().run_until_complete(create_op())

    benchmark.pedantic(run, rounds=50, iterations=10)
