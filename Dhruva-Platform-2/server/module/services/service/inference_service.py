import base64
import io
import json
import time
import traceback
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import soundfile as sf
from celery_backend.tasks import log_data
from custom_metrics import INFERENCE_REQUEST_COUNT, INFERENCE_REQUEST_DURATION_SECONDS
from exception.base_error import BaseError
from exception.client_error import ClientError
from exception.null_value_error import NullValueError
from fastapi import Depends, Request, status
from pydub import AudioSegment
from schema.services.common import (
    LANG_CODE_TO_SCRIPT_CODE,
    AudioFormat,
    _ULCAAudio,
    _ULCABaseAudioConfig,
    _ULCALanguage,
    _ULCATaskType,
    _ULCATextNBest,
)
from schema.services.common.ulca_text_n_best import _NBestToken
from schema.services.request import (
    ULCAAsrInferenceRequest,
    ULCAGenericInferenceRequest,
    ULCAInferenceRequest,
    ULCALLMInferenceRequest,
    ULCANerInferenceRequest,
    ULCAPipelineInferenceRequest,
    ULCATranslationInferenceRequest,
    ULCATransliterationInferenceRequest,
    ULCATtsInferenceRequest,
    ULCAVadInferenceRequest,
)
from schema.services.request.ulca_asr_inference_request import ULCATextFormat
from schema.services.request.ulca_vad_inference_request import (
    _ULCAVadInferenceRequestConfig,
)
from schema.services.response import (
    ULCAAsrInferenceResponse,
    ULCAInferenceResponse,
    ULCALLMInferenceResponse,
    ULCANerInferenceResponse,
    ULCAPipelineInferenceResponse,
    ULCATranslationInferenceResponse,
    ULCATransliterationInferenceResponse,
    ULCATtsInferenceResponse,
    ULCAVadInferenceResponse,
)
from schema.services.response.ulca_vad_inference_response import _ULCATimestamps
from scipy.io import wavfile

from ..error.errors import Errors
from ..gateway import InferenceGateway
from ..model import Model, ModelCache, Service, ServiceCache
from ..repository import ModelRepository, ServiceRepository
from .audio_service import AudioService
from .post_processor_service import PostProcessorService
from .subtitle_service import SubtitleService
from .triton_utils_service import TritonUtilsService


def populate_service_cache(serviceId: str, service_repository: ServiceRepository):
    service = service_repository.get_by_service_id(serviceId)
    service_cache = ServiceCache(**service.dict())
    service_cache.save()
    return service_cache


def populate_model_cache(modelId: str, model_repository: ModelRepository):
    model = model_repository.get_by_id(modelId)
    model_cache = ModelCache(**model.dict())
    model_cache.save()
    return model_cache


def validate_service_id(serviceId: str, service_repository):
    try:
        service = ServiceCache.get(serviceId)
    except Exception:
        try:
            service = populate_service_cache(serviceId, service_repository)
        except NullValueError:
            raise ClientError(
                status_code=status.HTTP_404_NOT_FOUND, message="Invalid Service Id"
            )
        except Exception:
            raise BaseError(Errors.DHRUVA104.value, traceback.format_exc())

    return service


def validate_model_id(modelId: str, model_repository):
    try:
        model = ModelCache.get(modelId)
    except Exception:
        try:
            model = populate_model_cache(modelId, model_repository)
        except Exception:
            raise BaseError(Errors.DHRUVA105.value, traceback.format_exc())

    return model


class InferenceService:
    def __init__(
        self,
        service_repository: ServiceRepository = Depends(ServiceRepository),
        model_repository: ModelRepository = Depends(ModelRepository),
        inference_gateway: InferenceGateway = Depends(InferenceGateway),
        subtitle_service: SubtitleService = Depends(SubtitleService),
        post_processor_service: PostProcessorService = Depends(PostProcessorService),
        audio_service: AudioService = Depends(AudioService),
        triton_utils_service: TritonUtilsService = Depends(TritonUtilsService),
    ) -> None:
        self.service_repository = service_repository
        self.model_repository = model_repository
        self.inference_gateway = inference_gateway
        self.subtitle_service = subtitle_service
        self.post_processor_service = post_processor_service
        self.audio_service = audio_service
        self.triton_utils_service = triton_utils_service

    async def run_inference(
        self, request: ULCAInferenceRequest, api_key_name: str, user_id: str
    ) -> ULCAInferenceResponse:
        serviceId = request.config.serviceId
        service = validate_service_id(serviceId, self.service_repository)
        model = validate_model_id(service.modelId, self.model_repository)  # type: ignore

        task_type = model.task_type  # type: ignore
        request_body = request.dict()

        match task_type:
            case _ULCATaskType.TRANSLATION:
                request_obj = ULCATranslationInferenceRequest(**request_body)
                return await self.run_translation_triton_inference(
                    request_obj, api_key_name, user_id
                )
            case _ULCATaskType.TRANSLITERATION:
                request_obj = ULCATransliterationInferenceRequest(**request_body)
                return await self.run_transliteration_triton_inference(
                    request_obj, api_key_name, user_id
                )
            case _ULCATaskType.ASR:
                request_obj = ULCAAsrInferenceRequest(**request_body)
                return await self.run_asr_triton_inference(
                    request_obj, api_key_name, user_id
                )
            case _ULCATaskType.TTS:
                request_obj = ULCATtsInferenceRequest(**request_body)
                return await self.run_tts_triton_inference(
                    request_obj, api_key_name, user_id
                )
            case _ULCATaskType.NER:
                request_obj = ULCANerInferenceRequest(**request_body)
                return await self.run_ner_triton_inference(
                    request_obj, api_key_name, user_id
                )
            case _ULCATaskType.TEXT_GENERATION:
                request_obj = ULCALLMInferenceRequest(**request_body)
                return await self.run_llm_inference(
                    request_obj, api_key_name, user_id
                )
            case _:
                raise BaseError(Errors.DHRUVA115.value)

    async def run_asr_triton_inference(
        self, request_body: ULCAAsrInferenceRequest, api_key_name: str, user_id: str
    ) -> ULCAAsrInferenceResponse:
        INFERENCE_REQUEST_COUNT.labels(
            api_key_name,
            user_id,
            request_body.config.serviceId,
            "asr",
            request_body.config.language.sourceLanguage,
            None,
        ).inc()

        serviceId = request_body.config.serviceId

        service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
        headers = {"Authorization": "Bearer " + service.api_key}

        language = request_body.config.language.sourceLanguage
        lm_enabled = (
            "lm" in request_body.config.postProcessors
            if request_body.config.postProcessors
            else False
        )
        if request_body.config.bestTokenCount == 0:
            model_name = "asr_am_lm_ensemble" if lm_enabled else "asr_am_ensemble"
        else:
            model_name = "asr_am_topk_ensemble"

        standard_rate = 16000

        res = ULCAAsrInferenceResponse(output=[])
        for input in request_body.audio:
            file_bytes = self.__get_audio_bytes(input)
            file_handle = io.BytesIO(file_bytes)

            final_audio = self.__process_audio_input(file_handle, standard_rate)

            # TODO: Specialised chunked inference for Whisper since it is unstable for long audio at high throughput
            batch_size = 1 if "whisper" in serviceId else 32

            pre_processors = (
                []
                if not request_body.config.preProcessors
                else request_body.config.preProcessors
            )

            (
                audio_chunks,
                speech_timestamps,
            ) = self.__run_asr_pre_processors(final_audio, pre_processors)

            transcript_lines: List[
                Tuple[Union[str, Dict[str, float]], Dict[str, float]]
            ] = []
            for i in range(0, len(audio_chunks), batch_size):
                batch = audio_chunks[i : i + batch_size]
                inputs, outputs = self.triton_utils_service.get_asr_io_for_triton(
                    batch, serviceId, language, request_body.config.bestTokenCount
                )

                with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                    api_key_name,
                    user_id,
                    request_body.config.serviceId,
                    "asr",
                    request_body.config.language.sourceLanguage,
                    None,
                ).time():
                    response = self.inference_gateway.send_triton_request(
                        url=service.endpoint,
                        model_name=model_name,
                        input_list=inputs,
                        output_list=outputs,
                        headers=headers,
                    )

                encoded_result = response.as_numpy("TRANSCRIPTS")
                if encoded_result is None:
                    encoded_result = np.array([])

                transcript_lines.extend(
                    [
                        (result.decode("utf-8"), speech_timestamps[i + idx])
                        for idx, result in enumerate(encoded_result.tolist())
                    ]
                )

            transcript_source_lines: List[Tuple[str, Dict[str, float]]] = (
                transcript_lines  # type: ignore
            )
            n_best_tokens: List[_NBestToken] = []

            if request_body.config.bestTokenCount > 0:
                transcript_source_lines: List[Tuple[str, Dict[str, float]]] = []
                for transcript_line in transcript_lines:
                    js = json.loads(transcript_line[0])  # type: ignore
                    transcript_source_lines.append((js["source"], transcript_line[1]))
                    n_best_tokens.extend(js["nBestTokens"])

            if request_body.config.postProcessors:
                transcript_source_lines = await self.__run_asr_post_processors(
                    transcript_source_lines,
                    request_body.config.postProcessors,
                    request_body.config.language.sourceLanguage,
                )

            transcript = self.__create_asr_response_format(
                transcript_source_lines, request_body.config.transcriptionFormat.value
            )

            res.output.append(
                _ULCATextNBest(
                    source=transcript.strip(),
                    nBestTokens=n_best_tokens if n_best_tokens else None,
                )
            )

        return res

    async def run_translation_triton_inference(
        self,
        request_body: ULCATranslationInferenceRequest,
        api_key_name: str,
        user_id: str,
    ) -> ULCATranslationInferenceResponse:
        INFERENCE_REQUEST_COUNT.labels(
            api_key_name,
            user_id,
            request_body.config.serviceId,
            "translation",
            request_body.config.language.sourceLanguage,
            request_body.config.language.targetLanguage,
        ).inc()

        serviceId = request_body.config.serviceId

        service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
        headers = {"Authorization": "Bearer " + service.api_key}

        source_lang = request_body.config.language.sourceLanguage
        target_lang = request_body.config.language.targetLanguage

        # TODO: Make Triton itself accept script-code separately
        if (
            request_body.config.language.sourceScriptCode
            and source_lang in LANG_CODE_TO_SCRIPT_CODE
            and request_body.config.language.sourceScriptCode
            != LANG_CODE_TO_SCRIPT_CODE[source_lang]
        ):
            source_lang += "_" + request_body.config.language.sourceScriptCode

        if (
            request_body.config.language.targetScriptCode
            and target_lang in LANG_CODE_TO_SCRIPT_CODE
            and request_body.config.language.targetScriptCode
            != LANG_CODE_TO_SCRIPT_CODE[target_lang]
        ):
            target_lang += "_" + request_body.config.language.targetScriptCode

        input_texts = [
            input.source.replace("\n", " ").strip() if input.source else " "
            for input in request_body.input
        ]

        max_batch_size = 90
        output_batch = []
        for i in range(0, len(input_texts), max_batch_size):
            inputs, outputs = self.triton_utils_service.get_translation_io_for_triton(
                input_texts[i : i + max_batch_size], source_lang, target_lang
            )

            with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                api_key_name,
                user_id,
                request_body.config.serviceId,
                "translation",
                request_body.config.language.sourceLanguage,
                request_body.config.language.targetLanguage,
            ).time():
                response = self.inference_gateway.send_triton_request(
                    url=service.endpoint,
                    model_name="nmt",
                    input_list=inputs,
                    output_list=outputs,
                    headers=headers,
                )

            encoded_result = response.as_numpy("OUTPUT_TEXT")
            if encoded_result is None:
                encoded_result = np.array([])

            output_batch.extend(encoded_result.tolist())

        results = []
        for source_text, result in zip(input_texts, output_batch):
            results.append({"source": source_text, "target": result[0].decode("utf-8")})

        return ULCATranslationInferenceResponse(output=results)

    async def run_transliteration_triton_inference(
        self,
        request_body: ULCATransliterationInferenceRequest,
        api_key_name: str,
        user_id: str,
    ) -> ULCATransliterationInferenceResponse:
        INFERENCE_REQUEST_COUNT.labels(
            api_key_name,
            user_id,
            request_body.config.serviceId,
            "transliteration",
            request_body.config.language.sourceLanguage,
            request_body.config.language.targetLanguage,
        ).inc()

        serviceId = request_body.config.serviceId

        service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
        headers = {"Authorization": "Bearer " + service.api_key}

        results = []
        source_lang = request_body.config.language.sourceLanguage
        target_lang = request_body.config.language.targetLanguage
        is_word_level = not request_body.config.isSentence
        top_k = request_body.config.numSuggestions

        if top_k and not is_word_level:
            raise ClientError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Topk is not valid for sentence level",
            )

        for input in request_body.input:
            input_string = input.source.replace("\n", " ").strip()
            if input_string:
                (
                    inputs,
                    outputs,
                ) = self.triton_utils_service.get_transliteration_io_for_triton(
                    input_string, source_lang, target_lang, is_word_level, top_k
                )

                with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                    api_key_name,
                    user_id,
                    request_body.config.serviceId,
                    "transliteration",
                    request_body.config.language.sourceLanguage,
                    request_body.config.language.targetLanguage,
                ).time():
                    response = self.inference_gateway.send_triton_request(
                        url=service.endpoint,
                        model_name="transliteration",
                        input_list=inputs,
                        output_list=outputs,
                        headers=headers,
                    )

                encoded_result = response.as_numpy("OUTPUT_TEXT")
                if encoded_result is None:
                    encoded_result = np.array([np.array([])])

                result = [r.decode("utf-8") for r in encoded_result.tolist()[0]]
            else:
                result = [input_string]

            results.append({"source": input_string, "target": result})

        return ULCATransliterationInferenceResponse(output=results)

    async def run_tts_triton_inference(
        self, request_body: ULCATtsInferenceRequest, api_key_name: str, user_id: str
    ) -> ULCATtsInferenceResponse:
        INFERENCE_REQUEST_COUNT.labels(
            api_key_name,
            user_id,
            request_body.config.serviceId,
            "tts",
            request_body.config.language.sourceLanguage,
            None,
        ).inc()

        serviceId = request_body.config.serviceId

        service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
        headers = {"Authorization": "Bearer " + service.api_key}

        ip_language = request_body.config.language.sourceLanguage
        ip_gender = request_body.config.gender.value
        standard_rate = 22050
        target_sr = (
            22050
            if not request_body.config.samplingRate
            else request_body.config.samplingRate
        )
        format = (
            "s16le"
            if request_body.config.audioFormat == AudioFormat.PCM
            else request_body.config.audioFormat.value
        )

        results = []

        for input in request_body.input:
            input_string = self.__process_tts_input(input.source)

            if input_string:
                sents = []
                if len(input_string) > 400:
                    words = input_string.split(" ")
                    tmp_sent = ""
                    for word in words:
                        if len(tmp_sent) + len(word) <= 400:
                            tmp_sent += " " + word
                        else:
                            sents.append(tmp_sent.strip())
                            tmp_sent = word

                    sents.append(tmp_sent)
                else:
                    sents.append(input_string)

                raw_audios = []
                for sent in sents:
                    inputs, outputs = self.triton_utils_service.get_tts_io_for_triton(
                        sent, ip_gender, ip_language
                    )

                    with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                        api_key_name,
                        user_id,
                        request_body.config.serviceId,
                        "tts",
                        request_body.config.language.sourceLanguage,
                        None,
                    ).time():
                        response = self.inference_gateway.send_triton_request(
                            url=service.endpoint,
                            model_name="tts",
                            input_list=inputs,
                            output_list=outputs,
                            headers=headers,
                        )

                    result = response.as_numpy("OUTPUT_GENERATED_AUDIO")
                    if result is None:
                        result = np.array([np.array([])])

                    raw_audios.append(result[0])

                if len(raw_audios) > 1:
                    raw_audio = np.concatenate(raw_audios)
                else:
                    raw_audio = raw_audios[0]

                final_audio = self.audio_service.resample_audio(
                    raw_audio, standard_rate, target_sr
                )

                if input.audioDuration:
                    cur_duration = len(final_audio) / target_sr
                    speed_factor = cur_duration / input.audioDuration

                    if speed_factor > 1:
                        final_audio = self.audio_service.stretch_audio(
                            final_audio, speed_factor, target_sr
                        )
                    elif speed_factor < 1:
                        final_audio = self.audio_service.append_silence(
                            final_audio, input.audioDuration - cur_duration, target_sr
                        )

                byte_io = io.BytesIO()
                wavfile.write(byte_io, target_sr, final_audio)

                if format != "wav":
                    audio = AudioSegment.from_file_using_temporary_files(byte_io)
                    request_body.config.audioLength
                    audio.export(byte_io, format=format)

                encoded_bytes = base64.b64encode(byte_io.read())
                encoded_string = encoded_bytes.decode()
            else:
                encoded_string = ""

            results.append(_ULCAAudio(audioContent=encoded_string))

        base_audio_config = _ULCABaseAudioConfig(
            language=_ULCALanguage(sourceLanguage=ip_language),
            audioFormat=request_body.config.audioFormat,
            encoding="base64",
            samplingRate=target_sr,
        )

        return ULCATtsInferenceResponse(audio=results, config=base_audio_config)

    async def run_ner_triton_inference(
        self, request_body: ULCANerInferenceRequest, api_key_name: str, user_id: str
    ) -> ULCANerInferenceResponse:
        INFERENCE_REQUEST_COUNT.labels(
            api_key_name,
            user_id,
            request_body.config.serviceId,
            "ner",
            request_body.config.language.sourceLanguage,
            None,
        ).inc()

        serviceId = request_body.config.serviceId

        service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
        headers = {"Authorization": "Bearer " + service.api_key}
        language = request_body.config.language.sourceLanguage
        input_texts = [
            input.source.replace("\n", " ").strip() if input.source else " "
            for input in request_body.input
        ]
        inputs, outputs = self.triton_utils_service.get_ner_io_for_triton(
            input_texts, language, model_name
        )

        # # TODO: Replace with real deployments
        # with INFERENCE_REQUEST_DURATION_SECONDS.labels(
        #     api_key_name,
        #     user_id,
        #     request_body.config.serviceId,
        #     "ner",
        #     request_body.config.language.sourceLanguage,
        #     None,
        # ).time():
        #     res = self.inference_gateway.send_inference_request(
        #         request_body=request_body, service=service
        #     )
        response = self.inference_gateway.send_triton_request(
            url=service.endpoint,
            model_name="ner",
            input_list=inputs,
            output_list=outputs,
            headers=headers,
        )
        encoded_result = response.as_numpy("OUTPUT_TEXT")
        if encoded_result is None:
            encoded_result = np.array([np.array([])])
        encoded_result = encoded_result.tolist()
        decoded_result = encoded_result.decode("utf-8")
        decoded_json_data = json.loads(decoded_result)

        final_result = [result["output"][0] for result in decoded_json_data]
        final_service_result =  ULCANerInferenceResponse(output=final_result)

        return final_service_result

    async def run_vad_triton_inference(
        self, request_body: ULCAVadInferenceRequest, api_key_name: str, user_id: str
    ):
        INFERENCE_REQUEST_COUNT.labels(
            api_key_name, user_id, request_body.config.serviceId, "vad", None, None
        ).inc()

        serviceId = request_body.config.serviceId

        service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
        headers = {"Authorization": "Bearer " + service.api_key}

        standard_rate = 16000

        res = ULCAVadInferenceResponse(output=[])

        for input in request_body.audio:
            file_bytes = self.__get_audio_bytes(input)
            file_handle = io.BytesIO(file_bytes)

            final_audio = self.__process_audio_input(
                file_handle, standard_rate, request_body.config.preProcessAudio
            )

            inputs, outputs = self.triton_utils_service.get_vad_io_for_triton(
                final_audio,
                standard_rate,
                threshold=request_body.config.threshold,
                min_silence_duration_ms=request_body.config.minSilenceDurationMs,
                speech_pad_ms=request_body.config.speechPadMs,
                min_speech_duration_ms=request_body.config.minSpeechDurationMs,
            )

            with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                api_key_name,
                user_id,
                request_body.config.serviceId,
                "vad",
                None,
                None,
            ).time():
                response = self.inference_gateway.send_triton_request(
                    url=service.endpoint,
                    model_name="vad",
                    input_list=inputs,
                    output_list=outputs,
                    headers=headers,
                )

            result = response.as_numpy("TIMESTAMPS")

            speech_timestamps: List[Dict[str, float]] = []

            if result is not None:
                speech_timestamps = json.loads(result[0].decode("utf-8"))

            if request_body.config.maxChunkDurationS:
                speech_timestamps = self.audio_service.adjust_timestamps(
                    speech_timestamps,
                    standard_rate,
                    request_body.config.maxChunkDurationS,
                )

            res.output.append(_ULCATimestamps(timestamps=speech_timestamps))

        return res

    async def run_pipeline_inference(
        self,
        request_body: ULCAPipelineInferenceRequest,
        request_state: Request,  # for request state
    ) -> ULCAPipelineInferenceResponse:
        results = []

        # Check if the pipeline construction is valid
        is_pipeline_valid = True
        for i in range(len(request_body.pipelineTasks) - 1):
            current_task_type, next_task_type = (
                request_body.pipelineTasks[i].taskType,
                request_body.pipelineTasks[i + 1].taskType,
            )
            if current_task_type == _ULCATaskType.ASR:
                if next_task_type not in {_ULCATaskType.TRANSLATION}:
                    is_pipeline_valid = False
                    break
            elif current_task_type == _ULCATaskType.TRANSLATION:
                if next_task_type not in {_ULCATaskType.TTS}:
                    is_pipeline_valid = False
                    break
            elif current_task_type == _ULCATaskType.TRANSLITERATION:
                if next_task_type not in {_ULCATaskType.TRANSLATION, _ULCATaskType.TTS}:
                    is_pipeline_valid = False
                    break
                if (
                    "isSentence" in request_body.pipelineTasks[i].config
                    and not request_body.pipelineTasks[i].config["isSentence"]
                ):
                    # Word-level does not make sense in pipeline
                    is_pipeline_valid = False
                    break
            else:
                is_pipeline_valid = False
                break

        if not is_pipeline_valid:
            # TODO: Return proper error messages once standardized
            return {"pipelineResponse": results}

        data_tracking_consent = False
        previous_output_json = request_body.inputData.dict()
        for pipeline_task in request_body.pipelineTasks:
            serviceId = (
                pipeline_task.config["serviceId"]
                if "serviceId" in pipeline_task.config
                else None
            )
            if not serviceId:
                serviceId = self.__auto_select_service_id(
                    pipeline_task.taskType, pipeline_task.config
                )

            start_time = time.perf_counter()
            new_request = ULCAGenericInferenceRequest(
                config=pipeline_task.config,
                **previous_output_json,
                controlConfig=request_body.controlConfig,
            )
            new_request.config.serviceId = serviceId

            error_msg, exception = None, None
            try:
                api_key_id = str(
                    request_state.state.api_key_id
                )  # Having this here to capture all errors
                previous_output_json = await self.run_inference(
                    request=new_request,
                    api_key_name=request_state.state.api_key_name,
                    user_id=request_state.state.user_id,
                )
            except BaseError as exc:
                exception = exc
                if exc.error_kind in (
                    Errors.DHRUVA101.value["kind"],
                    Errors.DHRUVA102.value["kind"],
                ):
                    error_msg = exc.error_kind + "_" + exc.error_message
            except Exception as other_exception:
                exception = other_exception
                error_msg = str(other_exception)

            if request_state.state._state.get("api_key_data_tracking"):
                data_tracking_consent = True
                if (
                    new_request.controlConfig
                    and new_request.controlConfig.dataTracking is False
                ):
                    data_tracking_consent = False

            log_data.apply_async(
                (
                    pipeline_task.taskType,
                    serviceId,
                    request_state.headers.get(
                        "X-Forwarded-For", request_state.client.host
                    ),
                    data_tracking_consent,
                    error_msg,
                    api_key_id,
                    new_request.json(),
                    # Error in first task will result in a dict, not pydantic model response
                    json.dumps(previous_output_json)
                    if isinstance(previous_output_json, dict)
                    else previous_output_json.json(),
                    time.perf_counter() - start_time,
                ),
                queue="data-log",
            )
            if exception:
                raise exception

            results.append(deepcopy(previous_output_json))

            # Output of previous will be input for next
            previous_output_json = previous_output_json.dict()
            previous_output_json.pop("config", None)
            if "output" in previous_output_json:
                previous_output_json["input"] = previous_output_json["output"]
                del previous_output_json["output"]

                if pipeline_task.taskType == _ULCATaskType.TRANSLATION:
                    # The output (target) of translation should be input (source) to next
                    for i in range(len(previous_output_json["input"])):
                        previous_output_json["input"][i]["source"] = (
                            previous_output_json["input"][i]["target"]
                        )
                        del previous_output_json["input"][i]["target"]
                elif pipeline_task.taskType == _ULCATaskType.TRANSLITERATION:
                    # The first output (target) of xlit should be input (source) to next
                    for i in range(len(previous_output_json["input"])):
                        previous_output_json["input"][i]["source"] = (
                            previous_output_json["input"][i]["target"][0]
                        )
                        del previous_output_json["input"][i]["target"]
            else:
                # This will ideally happen only for TTS, which is the final task supported *as of now*
                pass
        return {"pipelineResponse": results}

    def __get_audio_bytes(self, input: _ULCAAudio):
        try:
            if input.audioContent:
                file_bytes = base64.b64decode(input.audioContent)
            else:  # Either input audioContent or audioUri have to exist. Validation in Pydantic class.
                file_bytes = self.audio_service.download_audio(input.audioUri)  # type: ignore
        except Exception:
            raise BaseError(Errors.DHRUVA116.value, traceback.format_exc())

        return file_bytes

    def __process_audio_input(
        self, file_handle: io.BytesIO, standard_rate: int, process_audio: bool = True
    ):
        data, sampling_rate = sf.read(file_handle)
        data = data.tolist()
        raw_audio = np.array(data)  # in float64

        if not process_audio:
            return raw_audio

        mono_raw_audio = self.audio_service.stereo_to_mono(raw_audio)
        resampled_audio = self.audio_service.resample_audio(
            mono_raw_audio, sampling_rate, standard_rate
        )
        equalized_audio = self.audio_service.equalize_amplitude(
            resampled_audio, standard_rate
        )
        final_audio = self.audio_service.dequantize_audio(equalized_audio)

        return final_audio

    async def __run_asr_post_processors(
        self,
        transcript_lines: List[Tuple[str, Dict[str, float]]],
        post_processors: List[str],
        source_language: str,
    ):
        for idx, transcript_line in enumerate(transcript_lines):
            line = transcript_line[0]
            if "itn" in post_processors:
                line = await self.post_processor_service.run_itn(
                    line,
                    source_language,
                )

            if "punctuation" in post_processors:
                line = await self.post_processor_service.run_punctuation(
                    line,
                    source_language,
                )

            new_transcript_line = (line, transcript_line[1])
            transcript_lines[idx] = new_transcript_line

        return transcript_lines

    def __run_asr_pre_processors(self, audio: np.ndarray, pre_processors: List[str]):
        audio_chunks, speech_timestamps = (
            [audio],
            [
                {
                    "start": 0,
                    "start_secs": 0,
                    "end": len(audio),
                    "end_secs": round(len(audio) / 16000, 3),
                }
            ],
        )

        if "vad" in pre_processors:
            audio_chunks, speech_timestamps = self.audio_service.silero_vad_chunking(
                audio, 16000, 7
            )

        if "denoiser" in pre_processors:
            # call denoiser for every audio chunk
            pass

        return (audio_chunks, speech_timestamps)

    def __create_asr_response_format(
        self,
        transcript_lines: List[Tuple[str, Dict[str, float]]],
        transcription_format: ULCATextFormat,
    ):
        transcript = ""
        match transcription_format:
            case ULCATextFormat.SRT:
                transcript += self.subtitle_service.get_srt_subtitle(transcript_lines)
            case ULCATextFormat.WEBVTT:
                transcript += self.subtitle_service.get_webvtt_subtitle(
                    transcript_lines
                )
            case ULCATextFormat.TRANSCRIPT:
                for line in transcript_lines:
                    transcript += line[0].strip() + " "

        return transcript

    def __process_tts_input(self, text: str):
        processed_text = text.replace("।", ".").strip()
        return processed_text

    def __auto_select_service_id(
        self, task_type: _ULCATaskType, config: Dict[str, Any]
    ) -> str:
        match task_type:
            case _ULCATaskType.ASR:
                if config["language"]["sourceLanguage"] == "en":
                    serviceId = "ai4bharat/whisper-medium-en--gpu--t4"
                elif config["language"]["sourceLanguage"] == "hi":
                    serviceId = "ai4bharat/conformer-hi-gpu--t4"
                elif config["language"]["sourceLanguage"] in {"kn", "ml", "ta", "te"}:
                    serviceId = "ai4bharat/conformer-multilingual-dravidian-gpu--t4"
                else:
                    serviceId = "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4"
            case _ULCATaskType.TRANSLATION:
                serviceId = "ai4bharat/indictrans-v2-all-gpu--t4"
            case _ULCATaskType.TTS:
                if config["language"]["sourceLanguage"] in {"kn", "ml", "ta", "te"}:
                    serviceId = "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"
                elif config["language"]["sourceLanguage"] in {"en", "brx", "mni"}:
                    serviceId = "ai4bharat/indic-tts-coqui-misc-gpu--t4"
                else:
                    serviceId = "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"
            case _:
                raise BaseError(Errors.DHRUVA115.value)

        return serviceId

    async def run_pipeline_transliteration_inference(
        self,
        request_body: ULCAPipelineInferenceRequest,
        api_key_name: str,
        user_id: str,
    ) -> ULCAPipelineInferenceResponse:
        """Pipeline transliteration inference using Triton"""
        pipeline_responses = []
        
        for task in request_body.pipelineTasks:
            if task.taskType == "transliteration":
                serviceId = task.config.get("serviceId")
                
                # Try to validate service, but continue with mock if not found (for testing)
                try:
                    service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
                    headers = {"Authorization": "Bearer " + service.api_key}
                except (ClientError, BaseError):
                    # Service not found in DB - use mock for testing
                    service = None  # type: ignore
                    headers = {"Authorization": "Bearer mock_api_key"}
                
                INFERENCE_REQUEST_COUNT.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "transliteration",
                    task.config.get("language", {}).get("sourceLanguage", "unknown"),
                    task.config.get("language", {}).get("targetLanguage", "unknown"),
                ).inc()
                
                # Extract input data
                input_list = request_body.inputData.input if request_body.inputData.input else []
                
                # Prepare request for triton
                input_texts = [input_item.source for input_item in input_list]
                source_lang = task.config.get("language", {}).get("sourceLanguage", "en")
                target_lang = task.config.get("language", {}).get("targetLanguage", "hi")
                num_suggestions = task.config.get("numSuggestions", 7)
                
                # TODO: Replace with actual Triton inference call when endpoint is ready
                # For now, using dummy endpoint logic
                with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "transliteration",
                    source_lang,
                    target_lang,
                ).time():
                    # Placeholder for actual Triton call
                    # response = self.inference_gateway.send_triton_request(
                    #     url=service.endpoint,  # Real endpoint will be used here
                    #     model_name="transliteration",
                    #     input_list=inputs,
                    #     output_list=outputs,
                    #     headers=headers,
                    # )
                    
                    # Temporary mock response until real endpoint is available
                    output_list = []
                    for input_item in input_list:
                        # Mock transliteration output
                        mock_targets = ["की", "कि", "काई", "कीई", "काइ", "कीइ", "कै"][:num_suggestions]
                        output_list.append({
                            "source": input_item.source,
                            "target": mock_targets
                        })
                
                pipeline_responses.append({
                    "taskType": "transliteration",
                    "config": None,
                    "output": output_list,
                    "audio": None
                })
        
        return ULCAPipelineInferenceResponse(pipelineResponse=pipeline_responses)

    async def run_pipeline_ocr_inference(
        self,
        request_body: ULCAPipelineInferenceRequest,
        api_key_name: str,
        user_id: str,
    ) -> ULCAPipelineInferenceResponse:
        """Pipeline OCR inference using Triton"""
        pipeline_responses = []
        
        for task in request_body.pipelineTasks:
            if task.taskType == "ocr":
                serviceId = task.config.get("serviceId")
                
                # Try to validate service, but continue with mock if not found (for testing)
                try:
                    service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
                    headers = {"Authorization": "Bearer " + service.api_key}
                except (ClientError, BaseError):
                    # Service not found in DB - use mock for testing
                    service = None  # type: ignore
                    headers = {"Authorization": "Bearer mock_api_key"}
                
                source_language = task.config.get("language", {}).get("sourceLanguage", "en")
                
                INFERENCE_REQUEST_COUNT.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "ocr",
                    source_language,
                    "",
                ).inc()
                
                # Extract image data
                image_list = []
                if hasattr(request_body.inputData, 'image'):
                    image_list = request_body.inputData.image or []
                
                # TODO: Replace with actual Triton inference call when endpoint is ready
                with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "ocr",
                    source_language,
                    "",
                ).time():
                    # Placeholder for actual Triton call
                    # response = self.inference_gateway.send_triton_request(
                    #     url=service.endpoint,  # Real endpoint will be used here
                    #     model_name="ocr",
                    #     input_list=inputs,
                    #     output_list=outputs,
                    #     headers=headers,
                    # )
                    
                    # Temporary mock response until real endpoint is available
                    output_list = []
                    mock_text = "இது ஒரு மாதிரி தமிழ் உரை ஆகும்."
                    
                    if image_list:
                        for _ in image_list:
                            output_list.append({
                                "source": mock_text,
                                "target": ""
                            })
                    else:
                        output_list.append({
                            "source": mock_text,
                            "target": ""
                        })
                
                pipeline_responses.append({
                    "taskType": "ocr",
                    "config": None,
                    "output": output_list,
                    "audio": None
                })
        
        return ULCAPipelineInferenceResponse(pipelineResponse=pipeline_responses)

    async def run_pipeline_text_lang_detection_inference(
        self,
        request_body: ULCAPipelineInferenceRequest,
        api_key_name: str,
        user_id: str,
    ) -> ULCAPipelineInferenceResponse:
        """Pipeline text language detection inference using Triton"""
        pipeline_responses = []
        
        for task in request_body.pipelineTasks:
            if task.taskType == "txt-lang-detection":
                serviceId = task.config.get("serviceId")
                
                # Try to validate service, but continue with mock if not found (for testing)
                try:
                    service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
                    headers = {"Authorization": "Bearer " + service.api_key}
                except (ClientError, BaseError):
                    # Service not found in DB - use mock for testing
                    service = None  # type: ignore
                    headers = {"Authorization": "Bearer mock_api_key"}
                
                INFERENCE_REQUEST_COUNT.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "txt-lang-detection",
                    "",
                    "",
                ).inc()
                
                # Extract input data
                input_list = request_body.inputData.input if request_body.inputData.input else []
                
                # TODO: Replace with actual Triton inference call when endpoint is ready
                with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "txt-lang-detection",
                    "",
                    "",
                ).time():
                    # Placeholder for actual Triton call
                    # response = self.inference_gateway.send_triton_request(
                    #     url=service.endpoint,  # Real endpoint will be used here
                    #     model_name="text-lang-detection",
                    #     input_list=inputs,
                    #     output_list=outputs,
                    #     headers=headers,
                    # )
                    
                    # Temporary mock response until real endpoint is available
                    output_list = []
                    for input_item in input_list:
                        source_text = input_item.source if input_item.source else ""
                        
                        # Simple script detection for mock
                        if any('\u0B80' <= char <= '\u0BFF' for char in source_text):
                            lang_code, script_code = "ta", "Taml"
                        elif any('\u0900' <= char <= '\u097F' for char in source_text):
                            lang_code, script_code = "hi", "Deva"
                        else:
                            lang_code, script_code = "en", "Latn"
                        
                        output_list.append({
                            "source": source_text,
                            "langPrediction": [
                                {
                                    "langCode": lang_code,
                                    "scriptCode": script_code,
                                    "langScore": "0.95"
                                }
                            ]
                        })
                
                pipeline_responses.append({
                    "taskType": "txt-lang-detection",
                    "config": None,
                    "output": output_list,
                    "audio": None
                })
        
        return ULCAPipelineInferenceResponse(pipelineResponse=pipeline_responses)

    async def run_pipeline_audio_lang_detection_inference(
        self,
        request_body: ULCAPipelineInferenceRequest,
        api_key_name: str,
        user_id: str,
    ) -> ULCAPipelineInferenceResponse:
        """Pipeline audio language detection inference using Triton"""
        pipeline_responses = []
        
        for task in request_body.pipelineTasks:
            if task.taskType == "audio-lang-detection":
                serviceId = task.config.get("serviceId")
                
                # Try to validate service, but continue with mock if not found (for testing)
                try:
                    service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
                    headers = {"Authorization": "Bearer " + service.api_key}
                except (ClientError, BaseError):
                    # Service not found in DB - use mock for testing
                    service = None  # type: ignore
                    headers = {"Authorization": "Bearer mock_api_key"}
                
                INFERENCE_REQUEST_COUNT.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "audio-lang-detection",
                    "",
                    "",
                ).inc()
                
                # Extract audio data
                audio_list = request_body.inputData.audio if request_body.inputData.audio else []
                
                # TODO: Replace with actual Triton inference call when endpoint is ready
                with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "audio-lang-detection",
                    "",
                    "",
                ).time():
                    # Placeholder for actual Triton call
                    # response = self.inference_gateway.send_triton_request(
                    #     url=service.endpoint,  # Real endpoint will be used here
                    #     model_name="audio-lang-detection",
                    #     input_list=inputs,
                    #     output_list=outputs,
                    #     headers=headers,
                    # )
                    
                    # Temporary mock response until real endpoint is available
                    output_list = []
                    
                    for audio_item in audio_list:
                        audio_content = None
                        audio_uri = None
                        
                        if hasattr(audio_item, 'audioContent'):
                            audio_content = audio_item.audioContent
                        if hasattr(audio_item, 'audioUri'):
                            audio_uri = audio_item.audioUri
                        
                        # Mock language detection - defaulting to Hindi
                        output_list.append({
                            "audio": {
                                "audioContent": audio_content,
                                "audioUri": audio_uri
                            },
                            "langPrediction": [
                                {
                                    "langCode": "hi",
                                    "scriptCode": None,
                                    "langScore": None
                                }
                            ]
                        })
                    
                    if not output_list:
                        output_list.append({
                            "audio": {
                                "audioContent": None,
                                "audioUri": None
                            },
                            "langPrediction": [
                                {
                                    "langCode": "hi",
                                    "scriptCode": None,
                                    "langScore": None
                                }
                            ]
                        })
                
                pipeline_responses.append({
                "taskType": "audio-lang-detection",
                "config": None,
                "output": output_list,
                "audio": None
            })
        
        return ULCAPipelineInferenceResponse(pipelineResponse=pipeline_responses)

    async def run_pipeline_speaker_diarization_inference(
        self,
        request_body: ULCAPipelineInferenceRequest,
        api_key_name: str,
        user_id: str,
    ) -> ULCAPipelineInferenceResponse:
        """Pipeline speaker diarization inference using Triton"""
        pipeline_responses = []
        
        for task in request_body.pipelineTasks:
            if task.taskType == "speaker-diarization":
                serviceId = task.config.get("serviceId")
                
                # Try to validate service, but continue with mock if not found (for testing)
                try:
                    service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
                    headers = {"Authorization": "Bearer " + service.api_key}
                except (ClientError, BaseError):
                    # Service not found in DB - use mock for testing
                    service = None  # type: ignore
                    headers = {"Authorization": "Bearer mock_api_key"}
                
                INFERENCE_REQUEST_COUNT.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "speaker-diarization",
                    "",
                    "",
                ).inc()
                
                # Extract audio data
                audio_list = request_body.inputData.audio if request_body.inputData.audio else []
                
                # TODO: Replace with actual Triton inference call when endpoint is ready
                with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "speaker-diarization",
                    "",
                    "",
                ).time():
                    # Placeholder for actual Triton call
                    # response = self.inference_gateway.send_triton_request(
                    #     url=service.endpoint,  # Real endpoint will be used here
                    #     model_name="speaker-diarization",
                    #     input_list=inputs,
                    #     output_list=outputs,
                    #     headers=headers,
                    # )
                    
                    # Temporary mock response until real endpoint is available
                    output_list = []
                    
                    if audio_list:
                        for _ in audio_list:
                            # Mock speaker diarization output
                            output_list.append({
                                "speaker_labels": [
                                    {
                                        "speaker1": [
                                            {
                                                "start_time": 5.44,
                                                "duration": 1.58
                                            },
                                            {
                                                "start_time": 10.23,
                                                "duration": 2.15
                                            }
                                        ]
                                    },
                                    {
                                        "speaker2": [
                                            {
                                                "start_time": 7.02,
                                                "duration": 3.21
                                            }
                                        ]
                                    }
                                ]
                            })
                    else:
                        # If no audio provided, still return a mock response
                        output_list.append({
                            "speaker_labels": [
                                {
                                    "speaker1": [
                                        {
                                            "start_time": 5.44,
                                            "duration": 1.58
                                        }
                                    ]
                                }
                            ]
                        })
                
                pipeline_responses.append({
                    "taskType": "speaker-diarization",
                    "config": None,
                    "output": output_list,
                    "audio": None
                })
        
        return ULCAPipelineInferenceResponse(pipelineResponse=pipeline_responses)

    async def run_pipeline_language_diarization_inference(
        self,
        request_body: ULCAPipelineInferenceRequest,
        api_key_name: str,
        user_id: str,
    ) -> ULCAPipelineInferenceResponse:
        """Pipeline language diarization inference using Triton"""
        pipeline_responses = []
        
        for task in request_body.pipelineTasks:
            if task.taskType == "language-diarization":
                serviceId = task.config.get("serviceId")
                
                # Try to validate service, but continue with mock if not found (for testing)
                try:
                    service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
                    headers = {"Authorization": "Bearer " + service.api_key}
                except (ClientError, BaseError):
                    # Service not found in DB - use mock for testing
                    service = None  # type: ignore
                    headers = {"Authorization": "Bearer mock_api_key"}
                
                INFERENCE_REQUEST_COUNT.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "language-diarization",
                    "",
                    "",
                ).inc()
                
                # Extract audio data
                audio_list = request_body.inputData.audio if request_body.inputData.audio else []
                
                # TODO: Replace with actual Triton inference call when endpoint is ready
                with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "language-diarization",
                    "",
                    "",
                ).time():
                    # Placeholder for actual Triton call
                    # response = self.inference_gateway.send_triton_request(
                    #     url=service.endpoint,  # Real endpoint will be used here
                    #     model_name="language-diarization",
                    #     input_list=inputs,
                    #     output_list=outputs,
                    #     headers=headers,
                    # )
                    
                    # Temporary mock response until real endpoint is available
                    output_list = []
                    
                    if audio_list:
                        for _ in audio_list:
                            # Mock language diarization output with multiple languages detected
                            output_list.append({
                                "speaker_labels": [
                                    {
                                        "hindi": [
                                            {
                                                "start_time": 0.0,
                                                "duration": 5.44
                                            },
                                            {
                                                "start_time": 10.23,
                                                "duration": 3.15
                                            }
                                        ]
                                    },
                                    {
                                        "english": [
                                            {
                                                "start_time": 5.44,
                                                "duration": 4.79
                                            }
                                        ]
                                    },
                                    {
                                        "tamil": [
                                            {
                                                "start_time": 13.38,
                                                "duration": 2.62
                                            }
                                        ]
                                    }
                                ]
                            })
                    else:
                        # If no audio provided, still return a mock response
                        output_list.append({
                            "speaker_labels": [
                                {
                                    "hindi": [
                                        {
                                            "start_time": 0.0,
                                            "duration": 5.44
                                        }
                                    ]
                                }
                            ]
                        })
                
                pipeline_responses.append({
                    "taskType": "language-diarization",
                    "config": None,
                    "output": output_list,
                    "audio": None
                })
        
        return ULCAPipelineInferenceResponse(pipelineResponse=pipeline_responses)

    async def run_pipeline_speaker_verification_inference(
        self,
        request_body: ULCAPipelineInferenceRequest,
        api_key_name: str,
        user_id: str,
    ) -> ULCAPipelineInferenceResponse:
        """Pipeline speaker enrollment & verification inference using Triton"""
        pipeline_responses = []
        
        for task in request_body.pipelineTasks:
            if task.taskType == "speaker-verification":
                serviceId = task.config.get("serviceId")
                
                # Try to validate service, but continue with mock if not found (for testing)
                try:
                    service: Service = validate_service_id(serviceId, self.service_repository)  # type: ignore
                    headers = {"Authorization": "Bearer " + service.api_key}
                except (ClientError, BaseError):
                    # Service not found in DB - use mock for testing
                    service = None  # type: ignore
                    headers = {"Authorization": "Bearer mock_api_key"}
                
                INFERENCE_REQUEST_COUNT.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "speaker-verification",
                    "",
                    "",
                ).inc()
                
                # Extract audio data
                audio_list = request_body.inputData.audio if request_body.inputData.audio else []
                
                # Get operation type from config (enrollment or verification)
                operation = task.config.get("operation", "verification")  # "enrollment" or "verification"
                speaker_id = task.config.get("speakerId", None)
                
                # TODO: Replace with actual Triton inference call when endpoint is ready
                with INFERENCE_REQUEST_DURATION_SECONDS.labels(
                    api_key_name,
                    user_id,
                    serviceId,
                    "speaker-verification",
                    "",
                    "",
                ).time():
                    # Placeholder for actual Triton call
                    # response = self.inference_gateway.send_triton_request(
                    #     url=service.endpoint,  # Real endpoint will be used here
                    #     model_name="speaker-verification",
                    #     input_list=inputs,
                    #     output_list=outputs,
                    #     headers=headers,
                    # )
                    
                    # Temporary mock response until real endpoint is available
                    output_list = []
                    
                    if operation == "enrollment":
                        # Mock enrollment response
                        if audio_list:
                            for idx, _ in enumerate(audio_list):
                                output_list.append({
                                    "speakerId": f"speaker_{idx + 1}_{int(time.time())}",
                                    "enrollmentStatus": "success",
                                    "message": "Speaker enrolled successfully",
                                    "voiceprint": "mock_voiceprint_embedding_base64_encoded_string"
                                })
                        else:
                            output_list.append({
                                "speakerId": f"speaker_{int(time.time())}",
                                "enrollmentStatus": "success",
                                "message": "Speaker enrolled successfully",
                                "voiceprint": "mock_voiceprint_embedding_base64_encoded_string"
                            })
                    else:
                        # Mock verification response
                        if audio_list:
                            for _ in audio_list:
                                # Simulate verification with random confidence
                                is_verified = True
                                confidence_score = 0.92
                                
                                output_list.append({
                                    "speakerId": speaker_id if speaker_id else "unknown",
                                    "verified": is_verified,
                                    "confidence": confidence_score,
                                    "message": "Speaker verified successfully" if is_verified else "Speaker verification failed",
                                    "threshold": 0.75
                                })
                        else:
                            output_list.append({
                                "speakerId": speaker_id if speaker_id else "unknown",
                                "verified": False,
                                "confidence": 0.0,
                                "message": "No audio provided for verification",
                                "threshold": 0.75
                            })
                
                pipeline_responses.append({
                    "taskType": "speaker-verification",
                    "config": None,
                    "output": output_list,
                    "audio": None
                })
        
        return ULCAPipelineInferenceResponse(pipelineResponse=pipeline_responses)

    async def run_llm_inference(
        self, request_body: ULCALLMInferenceRequest, service_id: Optional[str], api_key_name: str, user_id: str
    ) -> ULCALLMInferenceResponse:
        if not service_id:
            raise ClientError(
                status_code=status.HTTP_400_BAD_REQUEST, message="serviceId is required"
            )

        # Extract input values from the request
        input_text = ""
        input_language = "en"
        output_language = "en"
        
        for input_item in request_body.inputs:
            if input_item.name == "INPUT_TEXT" and input_item.data:
                input_text = str(input_item.data[0]) if input_item.data else ""
            elif input_item.name == "INPUT_LANGUAGE_ID" and input_item.data:
                input_language = str(input_item.data[0]) if input_item.data else "en"
            elif input_item.name == "OUTPUT_LANGUAGE_ID" and input_item.data:
                output_language = str(input_item.data[0]) if input_item.data else "en"

        INFERENCE_REQUEST_COUNT.labels(
            api_key_name=api_key_name,
            user_id=user_id,
            inference_service=service_id,
            task_type="text-generation",
            source_language=input_language,
            target_language=output_language,
        ).inc()

        start_time = time.time()

        try:
            # Get the service
            service = self.service_repository.get_by_service_id(service_id)

            # Prepare the request in the new format (pass through as-is)
            llm_request = {
                "inputs": [input_item.dict() for input_item in request_body.inputs],
                "outputs": [output_item.dict() for output_item in request_body.outputs]
            }

            # Call the external LLM service
            response = self.inference_gateway.send_inference_request_dict(
                llm_request, service
            )

            # Process the response - it should already be in the correct format
            if not isinstance(response, dict):
                raise BaseError(Errors.DHRUVA101.value, "Invalid response format")

            # Validate response structure
            if "outputs" not in response:
                raise BaseError(Errors.DHRUVA101.value, "Response missing outputs")

            # Extract model_name and model_version from response or use defaults
            model_name = response.get("model_name", "llm")
            model_version = response.get("model_version", "1")
            outputs = response.get("outputs", [])

            duration = time.time() - start_time
            INFERENCE_REQUEST_DURATION_SECONDS.labels(
                api_key_name=api_key_name,
                user_id=user_id,
                inference_service=service_id,
                task_type="text-generation",
                source_language=input_language,
                target_language=output_language,
            ).observe(duration)

            # Convert outputs to response format
            from schema.services.response.ulca_llm_inference_response import LLMResponseOutput
            
            response_outputs = [
                LLMResponseOutput(
                    name=output.get("name", "OUTPUT_TEXT"),
                    datatype=output.get("datatype", "BYTES"),
                    shape=output.get("shape", [1, 1]),
                    data=output.get("data", [])
                )
                for output in outputs
            ]

            return ULCALLMInferenceResponse(
                model_name=model_name,
                model_version=model_version,
                outputs=response_outputs
            )

        except Exception as e:
            duration = time.time() - start_time
            INFERENCE_REQUEST_DURATION_SECONDS.labels(
                api_key_name=api_key_name,
                user_id=user_id,
                inference_service=service_id,
                task_type="text-generation",
                source_language=input_language,
                target_language=output_language,
            ).observe(duration)
            raise BaseError(Errors.DHRUVA101.value, traceback.format_exc())

