import asyncio
import os

from temporalio.client import Client

from workflow import MedicalRAGWorkflow

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")


async def main():

    client = await Client.connect(TEMPORAL_ADDRESS)

    result = await client.execute_workflow(
        MedicalRAGWorkflow.run,
        id="medical-rag-workflow",
        task_queue="medical-task-queue",
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())