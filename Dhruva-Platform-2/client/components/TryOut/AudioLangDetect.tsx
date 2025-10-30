import React, { useState } from "react";
import { Grid, GridItem, Stack, Button, Progress, Textarea, Text, Box } from "@chakra-ui/react";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";

interface Props {
  serviceId: string;
}

const AudioLangDetectTry: React.FC<Props> = (props) => {
  const [fetching, setFetching] = useState(false);
  const [response, setResponse] = useState("");
  const [predictions, setPredictions] = useState<any[]>([]);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = () => {
      const base64 = (reader.result as string).split(",")[1];
      runDetect(base64);
    };
  };

  const runDetect = async (base64Audio: string) => {
    setFetching(true);
    setResponse("");
    try {
      const res = await apiInstance.post(
        dhruvaAPI.pipelineAudioLangDetection + `?serviceId=${props.serviceId}`,
        {
          pipelineTasks: [{ taskType: "audio-lang-detection", config: { serviceId: props.serviceId } }],
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
      // parse pipelineResponse for lang predictions
      try {
        const pipelineResponse = res.data["pipelineResponse"] || res.data["output"] || res.data;
        const list: any[] = [];
        const arr = pipelineResponse[0]?.output || pipelineResponse[0] || pipelineResponse;
        if (Array.isArray(arr)) {
          arr.forEach((item: any) => {
            if (item.langPrediction) list.push(...item.langPrediction);
            else if (item.lang_prediction) list.push(...item.lang_prediction);
          });
        }
        setPredictions(list);
      } catch (e) {
        setPredictions([]);
      }
    } catch (e: any) {
      setResponse(String(e?.response?.data || e?.message || e));
    } finally {
      setFetching(false);
    }
  };

  return (
    <Grid templateRows="repeat(3)" gap={5}>
      <GridItem>{fetching ? <Progress size="xs" isIndeterminate /> : <></>}</GridItem>
      <GridItem>
        <Stack>
          <input
            type="file"
            accept="audio/*"
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
              e.currentTarget.value = null;
            }}
          />
          <Stack direction={"row"} spacing={4}>
            <Button onClick={() => setResponse("")}>Clear</Button>
          </Stack>
        </Stack>
      </GridItem>
      <GridItem>
        <Text fontWeight={600}>Response</Text>
        {predictions.length > 0 ? (
          <Stack spacing={2} mb={3}>
            {predictions.map((p, idx) => (
              <Box key={idx} p={2} bg="gray.50" borderRadius={6}>
                <Text>
                  {p.langCode} ({p.scriptCode}) — score: {p.langScore}
                </Text>
              </Box>
            ))}
          </Stack>
        ) : null}
        <Textarea readOnly value={response} rows={12} />
      </GridItem>
    </Grid>
  );
};

export default AudioLangDetectTry;
