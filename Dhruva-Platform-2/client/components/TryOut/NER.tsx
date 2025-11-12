import {
  Stack,
  Text,
  Select,
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
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { IndicTransliterate } from "@ai4bharat/indic-transliterate";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";
import { lang2label, tag2Color } from "../../config/config";
import React from "react";
import { FeedbackModal } from "../Feedback/Feedback";
import { PipelineInput, PipelineOutput } from "../Feedback/FeedbackTypes";

interface LanguageConfig {
  sourceLanguage: string;
  targetLanguage: string;
}

interface Props {
  languages: LanguageConfig[];
  serviceId: string;
}

const NERTry: React.FC<Props> = (props) => {
  const [languages, setLanguages] = useState<string[]>([]);
  const [language, setLanguage] = useState("hi");
  const [fetching, setFetching] = useState(false);
  const [tltText, setTltText] = useState("");
  const [fetched, setFetched] = useState(false);
  const [requestTime, setRequestTime] = useState("");
  const [nerTokens, setNERTokens] = useState<{ [key: string]: string }>({});
  const [pipelineInput, setPipelineInput] = useState<
    PipelineInput | undefined
  >();
  const [pipelineOutput, setPipelineOutput] = useState<
    PipelineOutput | undefined
  >();
  const getNEROutput = (source: string) => {
    setFetched(false);
    setFetching(true);
    apiInstance
      .post(
        dhruvaAPI.nerInference + `?serviceId=${props.serviceId}`,
        {
          input: [
            {
              source: source,
            },
          ],
          config: {
            language: {
              sourceLanguage: language,
            },
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
        const tokens = response.data["output"][0]["nerPrediction"];
        
        console.log("🔍 Backend NER Response:", tokens);
        
        // Backend already returns word-level tokens, just use them directly
        const tokenDictionary: { [key: string]: string } = {};
        tokens.forEach((token: any) => {
          tokenDictionary[token["token"]] = token["tag"];
        });
        
        console.log("📝 Token Dictionary:", tokenDictionary);
        
        setRequestTime(response.headers["request-duration"]);
        setNERTokens(tokenDictionary);
        setFetching(false);
        setFetched(true);
      });
  };

  useEffect(() => {
    const uniqueSourceLanguages: any = Array.from(
      new Set(
        props.languages.map(
          (language: LanguageConfig) => language.sourceLanguage
        )
      )
    );
    setLanguages(uniqueSourceLanguages);
    setLanguage(uniqueSourceLanguages[0]);
  }, []);

  const renderTransliterateComponent = () => {
    return (
      <IndicTransliterate
        renderComponent={(props) => (
          <Textarea resize="none" h={200} {...props} />
        )}
        onChangeText={(text: string) => {
          setTltText(text);
        }}
        value={tltText}
        placeholder="Type your text here for NER Inference..."
        lang={language}
        onChange={undefined}
        onBlur={undefined}
        onKeyDown={undefined}
        enabled={language !== "en"}
      />
    );
  };

  return (
    <Grid templateRows="repeat(3)" gap={5}>
      <GridItem>
        <Stack direction={"column"}>
          <Stack direction={"row"}>
            <Text className="dview-service-try-option-title">
              Select Language:
            </Text>
            <Select
              onChange={(e) => {
                setLanguage(e.target.value);
              }}
            >
              {languages.map((language) => (
                <option key={language} value={language}>
                  {lang2label[language]}
                </option>
              ))}
            </Select>
          </Stack>
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
        <Stack spacing={5}>
          {renderTransliterateComponent()}
          <Box
            p="1rem"
            borderRadius={15}
            bg={"gray.100"}
            resize="none"
            minH={200}
          >
            {Object.entries(nerTokens).map(([token, tag], idx) => {
              // Debug first
              if (idx === 0) {
                console.log("🎨 tag2Color object:", tag2Color);
                console.log(`🔍 Looking for tag: "${tag}"`, `Found:`, tag2Color[tag]);
              }
              
              // Fallback to "O" if tag is undefined or not in tag2Color
              const safeTag = (tag && tag2Color[tag]) ? tag : "O";
              
              return (
                <span
                  key={idx}
                  style={{
                    padding: 3,
                    backgroundColor: tag2Color[safeTag][0],
                    borderRadius: 15,
                    lineHeight: 1.8,
                    marginRight: 3,
                  }}
                >
                  {token}{" "}
                  <span
                    style={{
                      padding: 3,
                      backgroundColor: tag2Color[safeTag][1],
                      borderRadius: 15,
                      color: "white",
                    }}
                  >
                    {safeTag}
                  </span>
                </span>
              );
            })}
          </Box>
          <Stack direction={"column"} gap={5}>
            <Button
              onClick={() => {
                getNEROutput(tltText);
              }}
            >
              Generate
            </Button>
            {/* {fetched && (
              <FeedbackModal
                pipelineInput={pipelineInput}
                pipelineOutput={pipelineOutput}

              />
            )} */}
          </Stack>
        </Stack>
      </GridItem>
    </Grid>
  );
};

export default NERTry;
