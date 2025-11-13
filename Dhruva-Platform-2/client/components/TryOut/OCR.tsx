import {
  Stack,
  Text,
  Button,
  Progress,
  Grid,
  GridItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  Box,
  Image,
  Input,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  InputGroup,
  InputRightElement,
} from "@chakra-ui/react";
import { useState } from "react";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";
import React from "react";

interface Props {
  serviceId: string;
}

const OCRTry: React.FC<Props> = (props) => {
  const [fetching, setFetching] = useState(false);
  const [fetched, setFetched] = useState(false);
  const [requestTime, setRequestTime] = useState("");
  const [extractedText, setExtractedText] = useState("");
  const [imagePreview, setImagePreview] = useState<string>("");
  const [fileName, setFileName] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [loadingUrl, setLoadingUrl] = useState(false);
  const toast = useToast();

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith("image/")) {
        toast({
          title: "Invalid file type",
          description: "Please upload an image file (PNG, JPG, etc.)",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: "File too large",
          description: "Please upload an image smaller than 10MB",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      setFileName(file.name);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);

      // Convert to base64 for API
      const apiReader = new FileReader();
      apiReader.onload = () => {
        const base64 = (apiReader.result as string).split(",")[1]; // Remove data:image/...;base64, prefix
        runOCR(base64);
      };
      apiReader.readAsDataURL(file);
    }
  };

  const runOCR = (imageBase64: string) => {
    setFetched(false);
    setFetching(true);

    apiInstance
      .post(
        dhruvaAPI.ocrInference,
        {
          pipelineTasks: [
            {
              taskType: "ocr",
              config: {
                serviceId: props.serviceId,
                language: {
                  sourceLanguage: "hi", // Default to Hindi, can be made dynamic
                },
              },
            },
          ],
          inputData: {
            image: [
              {
                imageContent: imageBase64,
              },
            ],
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
        const pipelineResponse = response.data.pipelineResponse[0];
        
        if (pipelineResponse && pipelineResponse.output && pipelineResponse.output.length > 0) {
          const extractedText = pipelineResponse.output[0].source;
          setExtractedText(extractedText);
          setRequestTime(response.headers["request-duration"]);
          setFetched(true);
          
          toast({
            title: "OCR Complete!",
            description: "Text successfully extracted from image",
            status: "success",
            duration: 2000,
            isClosable: true,
          });
        } else {
          toast({
            title: "No text detected",
            description: "Could not extract text from the image",
            status: "warning",
            duration: 3000,
            isClosable: true,
          });
        }
        setFetching(false);
      })
      .catch((error) => {
        console.error("OCR Error:", error);
        toast({
          title: "OCR Failed",
          description: error.response?.data?.message || "An error occurred during OCR processing",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
        setFetching(false);
      });
  };

  const loadImageFromUrl = () => {
    if (!imageUrl.trim()) {
      toast({
        title: "Invalid URL",
        description: "Please enter a valid image URL",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setLoadingUrl(true);
    setImagePreview(imageUrl);
    setFileName(imageUrl.split("/").pop() || "image from URL");

    // Run OCR directly with imageUri
    runOCRFromUrl(imageUrl);
  };

  const runOCRFromUrl = (imageUri: string) => {
    setFetched(false);
    setFetching(true);

    apiInstance
      .post(
        dhruvaAPI.ocrInference,
        {
          pipelineTasks: [
            {
              taskType: "ocr",
              config: {
                serviceId: props.serviceId,
                language: {
                  sourceLanguage: "hi",
                },
              },
            },
          ],
          inputData: {
            image: [
              {
                imageUri: imageUri,
              },
            ],
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
        const pipelineResponse = response.data.pipelineResponse[0];
        
        if (pipelineResponse && pipelineResponse.output && pipelineResponse.output.length > 0) {
          const extractedText = pipelineResponse.output[0].source;
          setExtractedText(extractedText);
          setRequestTime(response.headers["request-duration"]);
          setFetched(true);
          
          toast({
            title: "OCR Complete!",
            description: "Text successfully extracted from image",
            status: "success",
            duration: 2000,
            isClosable: true,
          });
        } else {
          toast({
            title: "No text detected",
            description: "Could not extract text from the image",
            status: "warning",
            duration: 3000,
            isClosable: true,
          });
        }
        setFetching(false);
        setLoadingUrl(false);
      })
      .catch((error) => {
        console.error("OCR Error:", error);
        toast({
          title: "OCR Failed",
          description: error.response?.data?.message || "An error occurred during OCR processing",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
        setFetching(false);
        setLoadingUrl(false);
      });
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(extractedText);
    toast({
      title: "Copied!",
      description: "Text copied to clipboard",
      status: "success",
      duration: 2000,
      isClosable: true,
    });
  };

  return (
    <Grid templateRows="repeat(3)" gap={5}>
      <GridItem>
        <Stack direction={"row"}>
          <Text className="dview-service-try-option-title">
            Upload Image for OCR:
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
              <StatLabel>Characters Extracted</StatLabel>
              <StatNumber>{extractedText.length}</StatNumber>
              <StatHelpText>characters</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Response Time</StatLabel>
              <StatNumber>{(Number(requestTime) / 1000).toFixed(2)}</StatNumber>
              <StatHelpText>seconds</StatHelpText>
            </Stat>
          </SimpleGrid>
        </GridItem>
      ) : (
        <></>
      )}

      <GridItem>
        <Stack spacing={5}>
          <Tabs variant="enclosed" colorScheme="orange">
            <TabList>
              <Tab>Upload File</Tab>
              <Tab>Image URL</Tab>
            </TabList>

            <TabPanels>
              <TabPanel>
                <Stack direction={"column"} spacing={3}>
                  <Text fontSize="sm" color="gray.600">
                    Supported formats: PNG, JPG, JPEG, WebP (Max size: 10MB)
                  </Text>
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    p={1}
                    size="md"
                  />
                  {fileName && !imageUrl && (
                    <Text fontSize="sm" color="green.600">
                      ✓ {fileName}
                    </Text>
                  )}
                </Stack>
              </TabPanel>

              <TabPanel>
                <Stack direction={"column"} spacing={3}>
                  <Text fontSize="sm" color="gray.600">
                    Enter a publicly accessible image URL
                  </Text>
                  <InputGroup size="md">
                    <Input
                      placeholder="https://example.com/image.png"
                      value={imageUrl}
                      onChange={(e) => setImageUrl(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === "Enter") {
                          loadImageFromUrl();
                        }
                      }}
                    />
                    <InputRightElement width="4.5rem">
                      <Button
                        h="1.75rem"
                        size="sm"
                        onClick={loadImageFromUrl}
                        isLoading={loadingUrl}
                        colorScheme="orange"
                      >
                        Load
                      </Button>
                    </InputRightElement>
                  </InputGroup>
                  {fileName && imageUrl && (
                    <Text fontSize="sm" color="green.600">
                      ✓ Loaded from URL
                    </Text>
                  )}
                </Stack>
              </TabPanel>
            </TabPanels>
          </Tabs>

          {imagePreview && (
            <Box
              p="1rem"
              borderRadius={15}
              bg="gray.50"
              borderWidth={1}
              borderColor="gray.200"
            >
              <Text fontSize="sm" fontWeight="bold" mb={2}>
                Image Preview:
              </Text>
              <Image
                src={imagePreview}
                alt="Preview"
                maxH="300px"
                maxW="100%"
                objectFit="contain"
                borderRadius={10}
              />
            </Box>
          )}

          <Box
            p="1rem"
            borderRadius={15}
            bg="gray.50"
            minH={200}
            borderWidth={1}
            borderColor="gray.200"
          >
            <Stack direction="row" justify="space-between" align="center" mb={2}>
              <Text fontSize="sm" fontWeight="bold">
                Extracted Text:
              </Text>
              {extractedText && (
                <Button
                  size="sm"
                  colorScheme="orange"
                  variant="outline"
                  onClick={copyToClipboard}
                >
                  Copy
                </Button>
              )}
            </Stack>
            {extractedText ? (
              <Text fontSize="md" lineHeight="1.8" whiteSpace="pre-wrap">
                {extractedText}
              </Text>
            ) : (
              <Text fontSize="sm" color="gray.500" fontStyle="italic">
                No text extracted yet. Upload an image to see extracted text here.
              </Text>
            )}
          </Box>
        </Stack>
      </GridItem>
    </Grid>
  );
};

export default OCRTry;

