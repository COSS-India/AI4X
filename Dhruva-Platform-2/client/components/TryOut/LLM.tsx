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
  useToast,
  Box,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  HStack,
  VStack,
  Divider,
  Select,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";
import { getWordCount } from "../../utils/utils";
import React from "react";
import { FeedbackModal } from "../Feedback/Feedback";
import {
  PipelineInput,
  PipelineOutput,
  ULCATaskType,
} from "../Feedback/FeedbackTypes";
import { lang2label } from "../../config/config";

interface LanguageConfig {
  sourceLanguage: string;
  targetLanguage: string;
}

interface Props {
  languages: LanguageConfig[];
  serviceId: string;
}

const LLMTry: React.FC<Props> = (props) => {
  const [inputText, setInputText] = useState("");
  const [generatedText, setGeneratedText] = useState("");
  const [fetching, setFetching] = useState(false);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [requestDuration, setRequestDuration] = useState(0);
  const [inputLanguage, setInputLanguage] = useState("en");
  const [outputLanguage, setOutputLanguage] = useState("hi");
  const [modelParameters, setModelParameters] = useState({
    temperature: 0.7,
    max_tokens: 1000,
    top_p: 1.0,
  });

  const toast = useToast();

  // Initialize languages from props if available
  useEffect(() => {
    if (props.languages && props.languages.length > 0) {
      setInputLanguage(props.languages[0].sourceLanguage || "en");
      if (props.languages[0].targetLanguage) {
        setOutputLanguage(props.languages[0].targetLanguage);
      }
    }
  }, [props.languages]);

  const handleGenerate = async () => {
    if (!inputText.trim()) {
      toast({
        title: "Error",
        description: "Please enter some text to generate from",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setFetching(true);
    setGeneratedText("");
    setRequestDuration(0);

    try {
      const startTime = Date.now();
      const response = await apiInstance.post(
        `${dhruvaAPI.llmInference}?serviceId=${encodeURIComponent(props.serviceId)}`,
        {
          inputs: [
            {
              name: "INPUT_TEXT",
              datatype: "BYTES",
              shape: [1, 1],
              data: [inputText],
            },
            {
              name: "INPUT_LANGUAGE_ID",
              datatype: "BYTES",
              shape: [1, 1],
              data: [inputLanguage],
            },
            {
              name: "OUTPUT_LANGUAGE_ID",
              datatype: "BYTES",
              shape: [1, 1],
              data: [outputLanguage],
            },
          ],
          outputs: [{ name: "OUTPUT_TEXT" }],
        }
      );

      const endTime = Date.now();
      setRequestDuration(endTime - startTime);

      if (response.data && response.data.outputs && response.data.outputs.length > 0) {
        const outputData = response.data.outputs[0].data;
        if (outputData && outputData.length > 0) {
          setGeneratedText(String(outputData[0]));
        } else {
          setGeneratedText("No response generated");
        }
      } else {
        setGeneratedText("No response generated");
      }
    } catch (error: any) {
      console.error("LLM inference error:", error);
      toast({
        title: "Error",
        description: error.response?.data?.detail?.message || "Failed to generate text",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setFetching(false);
    }
  };

  const handleFeedback = () => {
    setIsFeedbackOpen(true);
  };

  const getFeedbackInput = (): PipelineInput => {
    return {
      pipelineTasks: [
        {
          taskType: ULCATaskType.TEXT_GENERATION,
          config: {
            serviceId: props.serviceId,
            model_parameters: modelParameters,
          },
        },
      ],
      inputData: {
        input: [{ source: inputText }],
      },
    };
  };

  const getFeedbackOutput = (): PipelineOutput => {
    return {
      pipelineResponse: [
        {
          taskType: ULCATaskType.TEXT_GENERATION,
          config: {
            serviceId: props.serviceId,
            model_parameters: modelParameters,
          },
          output: [{ source: generatedText }],
          audio: null,
        },
      ],
    };
  };

  // Get unique languages for selection
  const uniqueSourceLanguages = Array.from(
    new Set(props.languages.map((lang) => lang.sourceLanguage))
  );
  const uniqueTargetLanguages = Array.from(
    new Set(
      props.languages
        .map((lang) => lang.targetLanguage)
        .filter((lang) => lang !== undefined)
    )
  );

  return (
    <Stack spacing={6}>
      <VStack spacing={4} align="stretch">
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          <FormControl>
            <FormLabel fontSize="sm" fontWeight="bold">
              Input Language
            </FormLabel>
            <Select
              value={inputLanguage}
              onChange={(e) => setInputLanguage(e.target.value)}
            >
              {uniqueSourceLanguages.map((lang) => (
                <option key={lang} value={lang}>
                  {lang2label[lang] || lang}
                </option>
              ))}
            </Select>
          </FormControl>

          <FormControl>
            <FormLabel fontSize="sm" fontWeight="bold">
              Output Language
            </FormLabel>
            <Select
              value={outputLanguage}
              onChange={(e) => setOutputLanguage(e.target.value)}
            >
              {uniqueTargetLanguages.length > 0 ? (
                uniqueTargetLanguages.map((lang) => (
                  <option key={lang} value={lang}>
                    {lang2label[lang] || lang}
                  </option>
                ))
              ) : (
                <option value="hi">Hindi</option>
              )}
            </Select>
          </FormControl>
        </SimpleGrid>

        <FormControl>
          <FormLabel fontSize="sm" fontWeight="bold">
            Input Text
          </FormLabel>
          <Textarea
            placeholder="Enter your prompt here... (e.g., 'Hello how are you')"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={4}
            resize="vertical"
          />
        </FormControl>

        <Box>
          <Text fontSize="sm" fontWeight="bold" mb={2}>
            Model Parameters
          </Text>
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
            <FormControl>
              <FormLabel fontSize="xs">Temperature</FormLabel>
              <NumberInput
                value={modelParameters.temperature}
                onChange={(_, value) =>
                  setModelParameters({ ...modelParameters, temperature: value || 0.7 })
                }
                min={0}
                max={2}
                step={0.1}
                precision={1}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl>
              <FormLabel fontSize="xs">Max Tokens</FormLabel>
              <NumberInput
                value={modelParameters.max_tokens}
                onChange={(_, value) =>
                  setModelParameters({ ...modelParameters, max_tokens: value || 1000 })
                }
                min={1}
                max={4000}
                step={50}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl>
              <FormLabel fontSize="xs">Top P</FormLabel>
              <NumberInput
                value={modelParameters.top_p}
                onChange={(_, value) =>
                  setModelParameters({ ...modelParameters, top_p: value || 1.0 })
                }
                min={0}
                max={1}
                step={0.1}
                precision={1}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>
          </SimpleGrid>
        </Box>

        <Button
          colorScheme="orange"
          onClick={handleGenerate}
          isLoading={fetching}
          loadingText="Generating..."
          isDisabled={!inputText.trim()}
        >
          Generate Text
        </Button>
      </VStack>

      {fetching && (
        <Box>
          <Text fontSize="sm" mb={2}>
            Generating response...
          </Text>
          <Progress size="sm" isIndeterminate colorScheme="orange" />
        </Box>
      )}

      {generatedText && (
        <VStack spacing={4} align="stretch">
          <Divider />
          <FormControl>
            <FormLabel fontSize="sm" fontWeight="bold">
              Generated Text
            </FormLabel>
            <Textarea
              value={generatedText}
              readOnly
              rows={6}
              resize="vertical"
              bg="gray.50"
            />
          </FormControl>

          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
            <Stat>
              <StatLabel>Response Time</StatLabel>
              <StatNumber fontSize="lg">
                {requestDuration}ms
              </StatNumber>
              <StatHelpText>Request duration</StatHelpText>
            </Stat>

            <Stat>
              <StatLabel>Input Words</StatLabel>
              <StatNumber fontSize="lg">
                {getWordCount(inputText)}
              </StatNumber>
              <StatHelpText>Word count</StatHelpText>
            </Stat>

            <Stat>
              <StatLabel>Output Words</StatLabel>
              <StatNumber fontSize="lg">
                {getWordCount(generatedText)}
              </StatNumber>
              <StatHelpText>Generated words</StatHelpText>
            </Stat>
          </SimpleGrid>

          <HStack spacing={4}>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                navigator.clipboard.writeText(generatedText);
                toast({
                  title: "Copied",
                  description: "Generated text copied to clipboard",
                  status: "success",
                  duration: 2000,
                  isClosable: true,
                });
              }}
            >
              Copy Text
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleFeedback}
            >
              Provide Feedback
            </Button>
          </HStack>
        </VStack>
      )}

      <FeedbackModal
        isOpen={isFeedbackOpen}
        onClose={() => setIsFeedbackOpen(false)}
        input={getFeedbackInput()}
        output={getFeedbackOutput()}
      />
    </Stack>
  );
};

export default LLMTry;
