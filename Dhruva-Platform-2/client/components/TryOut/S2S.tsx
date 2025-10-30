import { Stack, Textarea, Button, Grid, GridItem, Select, Progress, Text } from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";
import { lang2label } from "../../config/config";
import React from "react";

interface LanguageConfig {
  sourceLanguage: string;
  targetLanguage: string;
}

interface Props {
  languages: LanguageConfig[];
  serviceId: string;
}

const S2STry: React.FC<Props> = (props) => {
  const [language, setLanguage] = useState("en");
  const [targetLanguage, setTargetLanguage] = useState("hi");
  const [responseText, setResponseText] = useState("");
  const [fetching, setFetching] = useState(false);

  useEffect(() => {
    if (props.languages && props.languages.length > 0) {
      setLanguage(props.languages[0].sourceLanguage || "en");
      setTargetLanguage(props.languages[0].targetLanguage || "hi");
    }
  }, [props.languages]);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = () => {
      const base64 = (reader.result as string).split(",")[1];
      runS2S(base64);
    };
  };

  const runS2S = (base64Audio: string) => {
    setFetching(true);
    apiInstance
      .post(
        dhruvaAPI.s2sInference + `?serviceId=${props.serviceId}`,
        {
          audio: [
            {
              audioContent: base64Audio,
            },
          ],
          config: {
            language: {
              sourceLanguage: language,
              targetLanguage: targetLanguage,
            },
            serviceId: props.serviceId,
          },
          controlConfig: { dataTracking: true },
        },
        {
          headers: {
            accept: "application/json",
            authorization: process.env.NEXT_PUBLIC_API_KEY,
            "Content-Type": "application/json",
          },
        }
      )
      .then((res) => {
        setResponseText(JSON.stringify(res.data, null, 2));
      })
      .catch((e) => {
        setResponseText(String(e?.response?.data || e.message || e));
      })
      .finally(() => setFetching(false));
  };

  return (
    <Grid templateRows="repeat(3)" gap={5}>
      <GridItem>
        <Stack direction={"row"} spacing={4}>
          <Text className="dview-service-try-option-title">Source:</Text>
          <Select value={language} onChange={(e) => setLanguage(e.target.value)}>
            {props.languages?.map((l) => (
              <option key={l.sourceLanguage} value={l.sourceLanguage}>
                {lang2label[l.sourceLanguage] || l.sourceLanguage}
              </option>
            ))}
          </Select>
          <Text className="dview-service-try-option-title">Target:</Text>
          <Select value={targetLanguage} onChange={(e) => setTargetLanguage(e.target.value)}>
            {props.languages?.map((l) => (
              <option key={l.targetLanguage} value={l.targetLanguage}>
                {lang2label[l.targetLanguage] || l.targetLanguage}
              </option>
            ))}
          </Select>
        </Stack>
      </GridItem>
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
          <Button
            onClick={() => {
              setResponseText("");
            }}
          >
            Clear
          </Button>
          <Textarea readOnly value={responseText} rows={12} />
        </Stack>
      </GridItem>
    </Grid>
  );
};

export default S2STry;
