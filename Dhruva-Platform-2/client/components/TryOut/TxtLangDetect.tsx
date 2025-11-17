import {
  Stack,
  Text,
  Button,
  Textarea,
  Progress,
  Grid,
  GridItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  Box,
  useToast,
} from "@chakra-ui/react";
import { useState } from "react";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";
import { getWordCount } from "../../utils/utils";
import React from "react";
import { FeedbackModal } from "../Feedback/Feedback";
import {
  PipelineInput,
  PipelineOutput,
  ULCATaskType,
} from "../Feedback/FeedbackTypes";

interface LanguageConfig {
  sourceLanguage: string;
  targetLanguage: string;
}

interface Props {
  languages: LanguageConfig[];
  serviceId: string;
}

const TxtLangDetectTry: React.FC<Props> = (props) => {
  const [inputText, setInputText] = useState("");
  const [detectedLanguage, setDetectedLanguage] = useState("");
  const [fetching, setFetching] = useState(false);
  const [fetched, setFetched] = useState(false);
  const [requestWordCount, setRequestWordCount] = useState(0);
  const [requestTime, setRequestTime] = useState("");
  const [pipelineInput, setPipelineInput] = useState<
    PipelineInput | undefined
  >();
  const [pipelineOutput, setPipelineOutput] = useState<
    PipelineOutput | undefined
  >();
  const toast = useToast();

  const detectLanguage = (source: string) => {
    if (!source.trim()) {
      toast({
        title: "Error",
        description: "Please enter some text to detect language",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setFetched(false);
    setFetching(true);
    setDetectedLanguage("");

    apiInstance
      .post(
        dhruvaAPI.txtLangDetectionInference + `?serviceId=${props.serviceId}`,
        {
          input: [
            {
              source: source,
            },
          ],
          config: {
            serviceId: props.serviceId,
          },
          controlConfig: {
            dataTracking: true,
          },
        },
        {
          headers: {
            accept: "application/json",
            authorization: process.env.NEXT_PUBLIC_API_KEY,
            "Content-Type": "application/json",
          },
        }
      )
      .then((response) => {
        // Parse dedicated text lang detection response
        const output = response.data["output"];
        if (output && output.length > 0) {
          const firstOutput = output[0];
          const langPrediction = firstOutput["langPrediction"];

          if (langPrediction && langPrediction.length > 0) {
            const prediction = langPrediction[0];
            // Use language field for full language name (e.g., "Sindhi (Latin script)")
            // Fallback to langCode if language is not available
            setDetectedLanguage(prediction["language"] || prediction["langCode"] || "");
          } else {
            // No prediction found
            setDetectedLanguage("");
          }
        } else {
          // Invalid response structure
          toast({
            title: "Warning",
            description: "Unexpected response format from server",
            status: "warning",
            duration: 3000,
            isClosable: true,
          });
        }

        setPipelineInput({
          pipelineTasks: [
            {
              taskType: ULCATaskType.TXT_LANG_DETECTION,
              config: {
                serviceId: props.serviceId,
              },
            },
          ],
          inputData: {
            input: [{ source: source }],
          },
        });

        setPipelineOutput({
          pipelineResponse: [
            {
              taskType: ULCATaskType.TXT_LANG_DETECTION,
              output: output || [],
            },
          ],
        });

        setRequestWordCount(getWordCount(inputText));
        setRequestTime(response.headers["request-duration"]);
        setFetching(false);
        setFetched(true);
      })
      .catch((error) => {
        console.error("Language detection error:", error);
        toast({
          title: "Error",
          description:
            error.response?.data?.detail?.message ||
            "Failed to detect language",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
        setFetching(false);
      });
  };

  const clearIO = () => {
    setInputText("");
    setDetectedLanguage("");
    setFetched(false);
  };

  return (
    <Grid templateRows="repeat(3)" gap={5}>
      <GridItem>
        <Stack direction={"row"}>
          <Text className="dview-service-try-option-title">
            Enter text to detect language:
          </Text>
        </Stack>
      </GridItem>
      <GridItem>
        {fetching ? <Progress size="xs" isIndeterminate /> : <></>}
      </GridItem>
      {fetched ? (
        <GridItem>
          <SimpleGrid
            p="1rem"
            w="100%"
            h="auto"
            bg="orange.100"
            borderRadius={15}
            columns={2}
            spacingX="40px"
            spacingY="20px"
          >
            <Stat>
              <StatLabel>Word Count</StatLabel>
              <StatNumber>{requestWordCount}</StatNumber>
              <StatHelpText>Input</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Response Time</StatLabel>
              <StatNumber>{Number(requestTime) / 1000}</StatNumber>
              <StatHelpText>seconds</StatHelpText>
            </Stat>
          </SimpleGrid>
        </GridItem>
      ) : (
        <></>
      )}
      <GridItem>
        <Stack>
          <Textarea
            value={inputText}
            onChange={(e) => {
              setInputText(e.target.value);
            }}
            w={"auto"}
            resize="none"
            h={200}
            placeholder="Type your text here to detect language..."
          />
          <Box
            p="1rem"
            borderRadius={15}
            bg={"gray.50"}
            minH={100}
            borderWidth={1}
            borderColor="gray.200"
          >
            <Text fontSize="sm" fontWeight="bold" mb={2}>
              Detected Language:
            </Text>
            {detectedLanguage ? (
              <Text fontSize="lg" fontWeight="semibold" color="orange.500">
                {detectedLanguage}
              </Text>
            ) : (
              <Text fontSize="sm" color="gray.500" fontStyle="italic">
                No language detected yet. Enter text and click "Detect Language" to see results.
              </Text>
            )}
          </Box>
          <Button
            onClick={() => {
              if (inputText.length > 0) {
                detectLanguage(inputText);
              } else {
                toast({
                  title: "Error",
                  description: "Please enter some text to detect language",
                  status: "error",
                  duration: 3000,
                  isClosable: true,
                });
              }
            }}
            colorScheme="orange"
            isLoading={fetching}
            loadingText="Detecting..."
            isDisabled={!inputText.trim()}
          >
            Detect Language
          </Button>
          {fetched && pipelineInput && pipelineOutput && (
            <FeedbackModal
              pipelineInput={pipelineInput}
              pipelineOutput={pipelineOutput}
              taskType={ULCATaskType.TXT_LANG_DETECTION}
            />
          )}
        </Stack>
      </GridItem>
    </Grid>
  );
};

export default TxtLangDetectTry;

