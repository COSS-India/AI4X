import React from "react";
import { useState } from "react";
import { Grid, GridItem, Stack, Button, Progress, Textarea, Text, Box, VStack } from "@chakra-ui/react";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";

interface Props { serviceId: string }

const SpeakerDiarizationTry: React.FC<Props> = (props) => {
  const [fetching, setFetching] = useState(false);
  const [response, setResponse] = useState("");
  const [segments, setSegments] = useState<any[]>([]);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = () => {
      const base64 = (reader.result as string).split(",")[1];
      runDiarize(base64);
    };
  };

  const runDiarize = async (base64Audio: string) => {
    setFetching(true);
    setResponse("");
    try {
      const res = await apiInstance.post(
        dhruvaAPI.pipelineSpeakerDiarization + `?serviceId=${props.serviceId}`,
        {
          pipelineTasks: [{ taskType: "speaker-diarization", config: { serviceId: props.serviceId } }],
          inputData: { audio: [{ audioContent: base64Audio }] },
          controlConfig: { dataTracking: true },
        },
        {
          headers: {
            accept: "application/json",
            authorization: process.env.NEXT_PUBLIC_API_KEY,
            "Content-Type": "application/json",
          },
        }
      );
      setResponse(JSON.stringify(res.data, null, 2));
      // parse for diarization segments
      try {
        const pipelineResponse = res.data["pipelineResponse"] || res.data["output"] || res.data;
        const arr = pipelineResponse[0]?.output || pipelineResponse[0] || pipelineResponse;
        const segs: any[] = [];
        if (Array.isArray(arr)) {
          arr.forEach((item: any) => {
            if (item.segments) segs.push(...item.segments);
            else if (item["speaker_segments"]) segs.push(...item["speaker_segments"]);
          });
        }
        setSegments(segs);
      } catch (e) {
        setSegments([]);
      }
    } catch (e: any) {
      setResponse(String(e?.response?.data || e?.message || e));
    } finally { setFetching(false); }
  };

  return (
    <Grid templateRows="repeat(3)" gap={5}>
      <GridItem>{fetching ? <Progress size="xs" isIndeterminate /> : <></>}</GridItem>
      <GridItem>
        <Stack>
          <input type="file" accept="audio/*" onChange={(e: any) => { const f = e.target.files?.[0]; if (f) handleFile(f); e.currentTarget.value = null; }} />
          <Button onClick={() => setResponse("")}>Clear</Button>
        </Stack>
      </GridItem>
      <GridItem>
        <Text fontWeight={600}>Response</Text>
        {segments.length > 0 ? (
          <VStack alignItems="stretch" spacing={2} mb={3}>
            {segments.map((s, idx) => (
              <Box key={idx} p={2} bg="gray.50" borderRadius={6}>
                <Text>
                  Speaker: {s.speaker || s.label} — {s.start_time || s.start} to {s.end_time || s.end}
                </Text>
                {s.text && <Text mt={2}>{s.text}</Text>}
              </Box>
            ))}
          </VStack>
        ) : null}
        <Textarea readOnly value={response} rows={12} />
      </GridItem>
    </Grid>
  );
};

export default SpeakerDiarizationTry;
