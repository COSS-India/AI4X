import React, { useEffect, useState } from "react";
import { Grid, GridItem, Stack, Textarea, Button, Progress, Text, Box } from "@chakra-ui/react";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";

interface LanguageConfig {
  sourceLanguage: string;
  targetLanguage?: string;
}

interface Props {
  languages: LanguageConfig[];
  serviceId: string;
}

const TxtLangDetectTry: React.FC<Props> = (props) => {
  const [inputText, setInputText] = useState<string>("");
  const [fetching, setFetching] = useState<boolean>(false);
  const [response, setResponse] = useState<string>("");
  const [predictions, setPredictions] = useState<any[]>([]);

  const runDetect = async () => {
    setFetching(true);
    setResponse("");
    try {
      const res = await apiInstance.post(
        dhruvaAPI.pipelineTextLangDetection + `?serviceId=${props.serviceId}`,
        {
          pipelineTasks: [
            { taskType: "txt-lang-detection", config: { serviceId: props.serviceId } },
          ],
          // GitBook expects inputData.input as the text array
          inputData: { input: [{ source: inputText }] },
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

      // Try to extract the useful output from pipelineResponse if present
      const pipelineResponse = res.data["pipelineResponse"] || res.data["output"] || res.data;
      setResponse(JSON.stringify(pipelineResponse, null, 2));
      // parse predictions if available
      try {
        const list: any[] = [];
        const arr = pipelineResponse[0]?.output || pipelineResponse[0]?.pipelineResponse || pipelineResponse;
        if (Array.isArray(arr)) {
          arr.forEach((item: any) => {
            if (item.langPrediction) {
              list.push(...item.langPrediction);
            } else if (item["langPrediction"]) {
              list.push(...item["langPrediction"]);
            }
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
          <Textarea value={inputText} onChange={(e) => setInputText(e.target.value)} h={200} placeholder="Paste text here for language detection..." />
          <Stack direction={"row"} spacing={4}>
            <Button onClick={() => setInputText("")}>Clear</Button>
            <Button colorScheme="orange" onClick={runDetect} isDisabled={!inputText}>Detect</Button>
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

export default TxtLangDetectTry;
