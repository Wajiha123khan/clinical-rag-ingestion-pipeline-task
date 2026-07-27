from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():

    from activities.read_dataset import read_dataset
    from activities.clean_dataset import clean_dataset
    from activities.chunk_dataset import chunk_dataset
    from activities.generate_embeddings import generate_embeddings
    from activities.store_pgvector import store_pgvector


@workflow.defn
class MedicalRAGWorkflow:

    @workflow.run
    async def run(self):

        data = await workflow.execute_activity(
            read_dataset,
            start_to_close_timeout=timedelta(minutes=2),
        )

        clean_data = await workflow.execute_activity(
            clean_dataset,
            data,
            start_to_close_timeout=timedelta(minutes=2),
        )

        chunks = await workflow.execute_activity(
            chunk_dataset,
            clean_data,
            start_to_close_timeout=timedelta(minutes=5),
        )

        embedded = await workflow.execute_activity(
            generate_embeddings,
            chunks,
            start_to_close_timeout=timedelta(minutes=90),
        )

        await workflow.execute_activity(
            store_pgvector,
            embedded,
            start_to_close_timeout=timedelta(minutes=5),
        )

        return "Done"