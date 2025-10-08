import csv
import io
import traceback

import requests
from fastapi import Depends
from uuid import UUID

from exception.base_error import BaseError
from schema.services.request import (
    FeedbackDownloadQuery,
    ULCAFeedbackQuestionRequest,
    ULCAFeedbackRequest,
)

from ..error.errors import Errors
from ..model import Feedback
from ..repository import FeedbackRepository


class FeedbackService:
    def __init__(
        self, feedback_repository: FeedbackRepository = Depends(FeedbackRepository)
    ):
        self.feedback_repository = feedback_repository

    def submit_feedback(self, request: ULCAFeedbackRequest, id: UUID):
        try:
            feedback = request.dict()
            feedback["user_id"] = id
            feedback["api_key_name"] = "default"
            feedback_obj = Feedback(**feedback)
            
            # Convert Pydantic model to SQLAlchemy model for database insertion
            from db.postgresql_models import Feedback as SQLFeedback
            sqlalchemy_feedback = SQLFeedback(
                user_id=feedback_obj.user_id,
                api_key_name=feedback_obj.api_key_name,
                feedback_timestamp=feedback_obj.feedbackTimeStamp,
                feedback_language=feedback_obj.feedbackLanguage,
                pipeline_input=feedback_obj.pipelineInput.dict() if feedback_obj.pipelineInput else None,
                pipeline_output=feedback_obj.pipelineOutput.dict() if feedback_obj.pipelineOutput else None,
                suggested_pipeline_output=feedback_obj.suggestedPipelineOutput.dict() if feedback_obj.suggestedPipelineOutput else None,
                pipeline_feedback=feedback_obj.pipelineFeedback.dict() if feedback_obj.pipelineFeedback else None,
                task_feedback=[task.dict() for task in feedback_obj.taskFeedback] if feedback_obj.taskFeedback else None
            )
            
            self.feedback_repository.insert_one(sqlalchemy_feedback)
            return {"message": "Feedback submitted successfully"}
        except Exception:
            raise BaseError(Errors.DHRUVA110.value, traceback.format_exc())

    def fetch_questions(self, request: ULCAFeedbackQuestionRequest):
        return requests.post(
            "https://dev-auth.ulcacontrib.org/ulca/mdms/v0/pipelineQuestions",
            json=request.dict(),
        ).json()

    def fetch_feedback_csv(self, params: FeedbackDownloadQuery):
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

        try:
            # Use SQLAlchemy query for PostgreSQL with date range filtering
            from sqlalchemy import and_
            from db.postgresql_models import Feedback as SQLFeedback
            
            # Get the database session from the repository
            db = self.feedback_repository.db
            
            # Build the query with proper SQLAlchemy filtering
            query = db.query(SQLFeedback).filter(
                and_(
                    SQLFeedback.feedback_timestamp >= params.fromDate,
                    SQLFeedback.feedback_timestamp <= params.toDate
                )
            )
            
            # Note: serviceId filter removed since Feedback model doesn't have service_id field
            # If you need to filter by service, you may need to add this field to the model
            # or filter through related tables
            
            feedback_docs = query.all()
            
        except Exception:
            raise BaseError(Errors.DHRUVA110.value, traceback.format_exc())

        file = io.StringIO()
        csv_writer = csv.writer(file)
        csv_writer.writerow(csv_headers)
        
        # Convert SQLAlchemy models to export rows
        for doc in feedback_docs:
            row = self._convert_to_export_row(doc)
            csv_writer.writerow(row)
        
        file.seek(0)
        return file

    def _convert_to_export_row(self, feedback_doc):
        """Convert SQLAlchemy Feedback model to export row format"""
        from datetime import datetime
        
        # Extract data from JSONB fields
        pipeline_input = feedback_doc.pipeline_input or {}
        pipeline_output = feedback_doc.pipeline_output or {}
        suggested_pipeline_output = feedback_doc.suggested_pipeline_output or {}
        pipeline_feedback = feedback_doc.pipeline_feedback or {}
        task_feedback = feedback_doc.task_feedback or []
        
        # Extract pipeline tasks and input data
        pipeline_tasks = pipeline_input.get('pipelineTasks', []) if pipeline_input else []
        input_data = pipeline_input.get('inputData') if pipeline_input else None
        
        # Extract pipeline responses
        pipeline_response = pipeline_output.get('pipelineResponse', []) if pipeline_output else []
        suggested_pipeline_response = suggested_pipeline_output.get('pipelineResponse', []) if suggested_pipeline_output else []
        
        # Extract feedback
        common_feedback = pipeline_feedback.get('commonFeedback', []) if pipeline_feedback else []
        
        # Convert timestamp to ISO format
        timestamp_str = datetime.utcfromtimestamp(int(feedback_doc.feedback_timestamp)).isoformat()
        
        row = [
            str(feedback_doc.id),
            timestamp_str,
            feedback_doc.feedback_language,
            pipeline_tasks,  # Already a list
            input_data,  # Already processed
            pipeline_response,  # Already a list
            suggested_pipeline_response,  # Already a list
            common_feedback,  # Already a list
            task_feedback,  # Already a list
        ]
        
        return row
