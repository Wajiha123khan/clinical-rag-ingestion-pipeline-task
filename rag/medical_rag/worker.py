from temporalio.client import Client
from temporalio.worker import Worker

from workflow import MedicalRAGWorkflow

from activities.read_dataset import read_dataset
from activities.clean_dataset import clean_dataset
from activities.chunk_dataset import chunk_dataset
from activities.generate_embeddings import generate_embeddings
from activities.store_pgvector import store_pgvector

import asyncio
import os

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")


async def main():

    client = await Client.connect(TEMPORAL_ADDRESS)

    worker = Worker(
        client,
        task_queue="medical-task-queue",
        workflows=[MedicalRAGWorkflow],
        activities=[
            read_dataset,
            clean_dataset,
            chunk_dataset,
            generate_embeddings,
            store_pgvector,
        ],
    )

    print("Worker Started...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())