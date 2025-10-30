import React, { useState } from "react";
import { Grid, GridItem, Stack, Button, Progress, Textarea, Text, Input, Box } from "@chakra-ui/react";
import { dhruvaAPI, apiInstance } from "../../api/apiConfig";

interface Props { serviceId: string }

const SpeakerVerificationTry: React.FC<Props> = (props) => {
  const [fetching, setFetching] = useState(false);
  const [response, setResponse] = useState("");
  const [enrollId, setEnrollId] = useState("");
  const [verification, setVerification] = useState<any | null>(null);

  const handleFile = (file: File, mode: "enroll" | "verify") => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = () => {
      const base64 = (reader.result as string).split(",")[1];
      runSV(base64, mode);
    };
  };

  const runSV = async (base64Audio: string, mode: "enroll" | "verify") => {
    setFetching(true);
    setResponse("");
    try {
      const payload: any = {
        pipelineTasks: [{ taskType: "speaker-verification", config: { serviceId: props.serviceId, mode } }],
        inputData: { audio: [{ audioContent: base64Audio }] },
        controlConfig: { dataTracking: true },
      };
      // enrollId may be required in config or inputData based on backend; include both to be safe
      if (enrollId) {
        payload["enrollId"] = enrollId;
        payload.inputData["enrollId"] = enrollId;
      }

  const res = await apiInstance.post(
        dhruvaAPI.pipelineSpeakerVerification + `?serviceId=${props.serviceId}`,
        payload,
        {
          headers: {
            accept: "application/json",
            authorization: process.env.NEXT_PUBLIC_API_KEY,
            "Content-Type": "application/json",
          },
        }
      );
      setResponse(JSON.stringify(res.data, null, 2));
      try {
        const pr = res.data["pipelineResponse"] || res.data["output"] || res.data;
        const out = pr[0]?.output || pr[0] || pr;
        // look for verification score
        if (Array.isArray(out)) {
          const v = out.find((o: any) => o.verification_score || o.score || o.similarity);
          setVerification(v || null);
        } else if (out.verification_score || out.score || out.similarity) {
          setVerification(out);
        } else setVerification(null);
      } catch (e) {
        setVerification(null);
      }
    } catch (e: any) {
      setResponse(String(e?.response?.data || e?.message || e));
    } finally { setFetching(false); }
  };

  return (
    <Grid templateRows="repeat(4)" gap={5}>
      <GridItem>{fetching ? <Progress size="xs" isIndeterminate /> : <></>}</GridItem>
      <GridItem>
        <Stack>
          <Input placeholder="Enrollment ID (for enroll/verify)" value={enrollId} onChange={(e) => setEnrollId(e.target.value)} />
          <input type="file" accept="audio/*" onChange={(e: any) => { const f = e.target.files?.[0]; if (f) handleFile(f, 'enroll'); e.currentTarget.value = null; }} />
          <Button onClick={() => setResponse("")}>Clear</Button>
          <Text>Use the file input above to Enroll (first) and then Verify using another file upload below.</Text>
          <input type="file" accept="audio/*" onChange={(e: any) => { const f = e.target.files?.[0]; if (f) handleFile(f, 'verify'); e.currentTarget.value = null; }} />
        </Stack>
      </GridItem>
      <GridItem>
        <Text fontWeight={600}>Response</Text>
        {verification ? (
          <Box p={2} bg="gray.50" borderRadius={6} mb={3}>
            <Text>Verification result:</Text>
            <Text>Score: {verification.verification_score || verification.score || verification.similarity}</Text>
          </Box>
        ) : null}
        <Textarea readOnly value={response} rows={12} />
      </GridItem>
    </Grid>
  );
};

export default SpeakerVerificationTry;
