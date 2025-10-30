import { Stack, Textarea, Button, Grid, GridItem, Progress, Text } from "@chakra-ui/react";
import { useState } from "react";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";
import React from "react";

interface Props {
  serviceId: string;
}

const VADTry: React.FC<Props> = (props) => {
  const [responseText, setResponseText] = useState("");
  const [fetching, setFetching] = useState(false);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = () => {
      const base64 = (reader.result as string).split(",")[1];
      runVAD(base64);
    };
  };

  const runVAD = (base64Audio: string) => {
    setFetching(true);
    apiInstance
      .post(
        dhruvaAPI.vadInference + `?serviceId=${props.serviceId}`,
        {
          audio: [
            {
              audioContent: base64Audio,
            },
          ],
          config: {
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
          <Button onClick={() => setResponseText("")}>Clear</Button>
          <Textarea readOnly value={responseText} rows={12} />
        </Stack>
      </GridItem>
    </Grid>
  );
};

export default VADTry;
