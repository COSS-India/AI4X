import csv
import io
import os
from datetime import datetime

from celery_backend.tasks.database import AppDatabase, LogDatastore
from module.services.repository.feedback_repository import FeedbackRepository
from db.postgresql_models import Feedback as SQLFeedback

from ..celery_app import app
from . import constants

feedback_store = LogDatastore()

csv_headers = [
    "ObjectId",
    "Feedback Timestamp",
    "Feedback Language",
    "Pipeline Tasks",
    "Input Data",
    "Pipeline Response",
    "Suggested Pipeline Response",
    "Pipeline Feedback",
    "Task Feedback",
]


@app.task(name="upload.feedback.dump")
def upload_feedback_dump() -> None:
    """Generates feedback dumps locally (cloud storage disabled for sandbox)"""
    print("[SANDBOX MODE] Feedback dump task running - cloud storage disabled")

    file = io.StringIO()
    csv_writer = csv.writer(file)
    csv_writer.writerow(csv_headers)

    d = datetime.now()

    start_month, start_year = (
        (d.month - 1, d.year) if d.month - 1 != 0 else (12, d.year - 1)
    )
    start_date = d.replace(
        year=start_year,
        month=start_month,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    end_date = d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Use PostgreSQL repository to query feedback
    try:
        db_session = AppDatabase()
        feedback_repo = FeedbackRepository(db_session)

        # Query feedback records within date range
        # Note: PostgreSQL uses created_at timestamp, not feedbackTimeStamp
        from sqlalchemy import and_
        feedback_records = db_session.query(SQLFeedback).filter(
            and_(
                SQLFeedback.created_at >= start_date,
                SQLFeedback.created_at < end_date
            )
        ).all()

        record_count = 0
        for feedback_record in feedback_records:
            # Convert PostgreSQL record to export format
            csv_writer.writerow([
                str(feedback_record.id),  # Use UUID instead of ObjectId
                feedback_record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "en",  # Default language
                str(feedback_record.pipeline_input) if feedback_record.pipeline_input else "",
                str(feedback_record.pipeline_input) if feedback_record.pipeline_input else "",
                str(feedback_record.pipeline_output) if feedback_record.pipeline_output else "",
                str(feedback_record.suggested_pipeline_output) if feedback_record.suggested_pipeline_output else "",
                str(feedback_record.pipeline_feedback) if feedback_record.pipeline_feedback else "",
                "",  # Task feedback placeholder
            ])
            record_count += 1

        db_session.close()

    except Exception as e:
        print(f"[ERROR] Failed to query feedback from PostgreSQL: {e}")
        record_count = 0

    # Save to local file instead of cloud storage
    local_file_name = f"feedback_dump_{start_year}{start_month:02d}_{d.strftime('%Y%m%d_%H%M%S')}.csv"
    local_file_path = os.path.join(constants.LOCAL_DATA_DIR, local_file_name)

    try:
        with open(local_file_path, 'w', newline='', encoding='utf-8') as f:
            f.write(file.getvalue())
        print(f"[LOCAL STORAGE] Feedback dump saved locally: {local_file_path} ({record_count} records)")
    except Exception as e:
        print(f"[ERROR] Failed to save feedback dump locally: {e}")

    return
