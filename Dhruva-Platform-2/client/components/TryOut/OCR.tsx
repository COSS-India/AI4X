import React, { useEffect, useState } from "react";
import {
  Grid,
  GridItem,
  Stack,
  Textarea,
  Button,
  Progress,
  Input,
  Checkbox,
  Text,
  Select,
  Image,
  Box,
  VStack,
} from "@chakra-ui/react";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";
import { lang2label } from "../../config/config";

interface LanguageConfig {
  sourceLanguage: string;
  targetLanguage?: string;
}

interface Props {
  languages: LanguageConfig[];
  serviceId: string;
}

const OCRTry: React.FC<Props> = (props) => {
  const [sourceLanguage, setSourceLanguage] = useState<string>(
    props.languages?.[0]?.sourceLanguage || "en"
  );
  const [imageUrl, setImageUrl] = useState<string>("");
  const [imageBase64, setImageBase64] = useState<string>("");
  const [textDetection, setTextDetection] = useState<boolean>(false);
  const [fetching, setFetching] = useState<boolean>(false);
  const [responseText, setResponseText] = useState<string>("");
  const [parsedTextLines, setParsedTextLines] = useState<string[]>([]);

  useEffect(() => {
    if (props.languages && props.languages.length > 0) {
      setSourceLanguage(props.languages[0].sourceLanguage || "en");
    }
  }, [props.languages]);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = () => {
      const base64 = (reader.result as string).split(",")[1];
      setImageBase64(base64);
      setImageUrl("");
    };
  };

  const runOCR = async () => {
    setFetching(true);
    setResponseText("");
    const pipelineTasks = [
      {
        taskType: "ocr",
        config: {
          language: { sourceLanguage: sourceLanguage },
          serviceId: props.serviceId,
          textDetection: textDetection ? "True" : "False",
        },
      },
    ];

    const inputData: any = { image: [] };
    if (imageUrl) {
      inputData.image.push({ imageUri: imageUrl });
    }
    if (imageBase64) {
      inputData.image.push({ imageContent: imageBase64 });
    }

    try {
      const res = await apiInstance.post(
        dhruvaAPI.pipelineOcr + `?serviceId=${props.serviceId}`,
        {
          pipelineTasks,
          inputData,
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

      setResponseText(JSON.stringify(res.data, null, 2));
      // Try to parse common OCR response shapes from Bhashini
      const lines: string[] = [];
      try {
        const outputArr = res.data["output"] || [];
        outputArr.forEach((o: any) => {
          // Some responses put recognized text under output[0].source
          if (o["output"]) {
            // pipeline style: o.output is array
            o.output.forEach((item: any) => {
              if (item["source"]) {
                lines.push(item["source"]);
              }
              if (item["target"]) {
                // target may be array of suggestions
                if (Array.isArray(item["target"])) {
                  item["target"].forEach((t: any) => {
                    if (t["source"]) lines.push(t["source"]);
                    if (t["target"]) lines.push(t["target"]);
                  });
                }
              }
            });
          } else if (o["source"]) {
            lines.push(o["source"]);
          }
        });
      } catch (e) {
        // ignore parse errors and fall back to raw JSON
      }

      setParsedTextLines(lines.filter(Boolean));
    } catch (e: any) {
      setResponseText(String(e?.response?.data || e?.message || e));
    } finally {
      setFetching(false);
    }
  };

  return (
    <Grid templateRows="repeat(3)" gap={5}>
      <GridItem>{fetching ? <Progress size="xs" isIndeterminate /> : <></>}</GridItem>
      <GridItem>
        <Stack spacing={4}>
          <Stack direction={"row"} alignItems="center">
            <Text className="dview-service-try-option-title">Language:</Text>
            <Select
              value={sourceLanguage}
              onChange={(e) => setSourceLanguage(e.target.value)}
            >
              {props.languages?.map((l) => (
                <option key={l.sourceLanguage} value={l.sourceLanguage}>
                  {lang2label[l.sourceLanguage] || l.sourceLanguage}
                </option>
              ))}
            </Select>
          </Stack>

          <Stack direction={["column", "row"]} alignItems="center" spacing={4}>
            <Input
              placeholder="Image URL"
              value={imageUrl}
              onChange={(e) => {
                setImageUrl(e.target.value);
                if (e.target.value) setImageBase64("");
              }}
            />
            <input
              type="file"
              accept="image/*"
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                const file = e.target.files?.[0];
                if (file) handleFile(file);
                e.currentTarget.value = null;
              }}
            />
          </Stack>

          <Stack direction={"row"} alignItems="center">
            <Checkbox
              isChecked={textDetection}
              onChange={(e) => setTextDetection(e.target.checked)}
            >
              Enable textDetection (word-detector)
            </Checkbox>
            <Button onClick={() => { setImageBase64(""); setImageUrl(""); setResponseText(""); }}>Clear</Button>
            <Button colorScheme="orange" onClick={runOCR} isDisabled={!imageUrl && !imageBase64}>
              Run OCR
            </Button>
          </Stack>
        </Stack>
      </GridItem>
      <GridItem>
        <VStack alignItems="stretch" spacing={4}>
          {imageBase64 || imageUrl ? (
            <Box>
              <Text fontWeight={600}>Preview</Text>
              <Image
                src={imageBase64 ? `data:image/*;base64,${imageBase64}` : imageUrl}
                alt="uploaded"
                maxH="360px"
                objectFit="contain"
                borderRadius={8}
              />
            </Box>
          ) : null}

          <Box>
            <Text fontWeight={600}>Parsed Text</Text>
            {parsedTextLines.length > 0 ? (
              <VStack alignItems="flex-start" spacing={2} mt={2}>
                {parsedTextLines.map((line, idx) => (
                  <Box key={idx} p={2} bg="gray.50" borderRadius={6} w="100%">
                    <Text whiteSpace="pre-wrap">{line}</Text>
                  </Box>
                ))}
              </VStack>
            ) : (
              <Textarea readOnly value={responseText} rows={12} />
            )}
          </Box>
        </VStack>
      </GridItem>
    </Grid>
  );
};

export default OCRTry;
