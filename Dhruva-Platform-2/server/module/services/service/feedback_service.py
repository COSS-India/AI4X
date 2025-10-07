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

        query = {
            "feedbackTimeStamp": {"$gte": params.fromDate, "$lte": params.toDate},
        }

        try:
            feedback_docs = self.feedback_repository.find(query)
        except Exception:
            raise BaseError(Errors.DHRUVA110.value, traceback.format_exc())

        file = io.StringIO()
        csv_writer = csv.writer(file)
        csv_writer.writerow(csv_headers)
        csv_writer.writerows(list(map(lambda doc: doc.to_export_row(), feedback_docs)))
        file.seek(0)

        return file
