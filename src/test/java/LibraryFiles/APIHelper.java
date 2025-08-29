package LibraryFiles;

import java.nio.file.Path;
import java.nio.file.Paths;
import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import java.security.cert.X509Certificate;
import java.util.Base64;
import java.io.*;
import java.nio.file.Files;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;

import org.json.JSONArray;
import org.json.JSONObject;

import TestCases.A_BaseSuiteFile;

public class APIHelper extends A_BaseSuiteFile {

	Path path = Paths.get(System.getProperty("user.dir"), "TestData", "APIData.properties");
	String dataFilePath = path.toString();

	Path recPath = Paths.get(System.getProperty("user.dir"), "TestData", "Recording.wav");
	String audioFilePath = recPath.toString();

	public void disableSSLCertificateChecking() throws Exception {
		TrustManager[] trustAllCerts = new TrustManager[] { new X509TrustManager() {
			public java.security.cert.X509Certificate[] getAcceptedIssuers() {
				return null;
			}

			public void checkClientTrusted(X509Certificate[] certs, String authType) {
			}

			public void checkServerTrusted(X509Certificate[] certs, String authType) {
			}
		} };

		SSLContext sc = SSLContext.getInstance("SSL");
		sc.init(null, trustAllCerts, new java.security.SecureRandom());
		HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());

		HostnameVerifier allHostsValid = (hostname, session) -> true;
		HttpsURLConnection.setDefaultHostnameVerifier(allHostsValid);
	}

	public Response callTtsApi(String inputText, String sourceLang, String gender) throws Exception {
		// Base URI
		RestAssured.baseURI = "https://13.203.149.17";

		// Construct request payload
		JSONObject payload = new JSONObject().put("controlConfig", new JSONObject().put("dataTracking", true))
				.put("config",
						new JSONObject().put("serviceId", "ai4bharat/indictts--gpu-t4").put("gender", gender)
								.put("samplingRate", 0).put("audioFormat", "wav").put("language",
										new JSONObject().put("sourceLanguage", sourceLang).put("sourceScriptCode", "")))
				.put("input", new org.json.JSONArray()
						.put(new JSONObject().put("source", inputText).put("audioDuration", 3)));

		// Make the API call
		return RestAssured.given().relaxedHTTPSValidation() // allows bypassing invalid SSL for IP-based HTTPS
				.contentType(ContentType.JSON).accept(ContentType.JSON).header("x-auth-source", "API_KEY")
				.header("Authorization", "CE6rrAxAIFglquUYZJaVClTlx7FjhxVWGXLE6sOnxIkqK1UE6a9-ojnRpZ7GJYma")
				.body(payload.toString()).when().post("/services/inference/tts").then().extract().response();
	}

	public Response callTtsApiForJson(String inputText, String sourceLang, String sourceScript) {
		RestAssured.baseURI = "https://13.203.149.17";

		JSONObject payload = new JSONObject().put("controlConfig", new JSONObject().put("dataTracking", true))
				.put("config",
						new JSONObject().put("serviceId", "ai4bharat/indictts--gpu-t4").put("gender", "male")
								.put("samplingRate", 0).put("audioFormat", "wav").put("language",
										new JSONObject().put("sourceLanguage", sourceLang).put("sourceScriptCode",
												sourceScript)))
				.put("input", new JSONArray().put(new JSONObject().put("source", inputText).put("audioDuration", 4)));

		return RestAssured.given().relaxedHTTPSValidation().contentType(ContentType.JSON).accept(ContentType.JSON)
				.header("x-auth-source", "API_KEY")
				.header("Authorization", "CE6rrAxAIFglquUYZJaVClTlx7FjhxVWGXLE6sOnxIkqK1UE6a9-ojnRpZ7GJYma")
				.body(payload.toString()).when().post("/services/inference/tts").then().extract().response();
	}

	public Response callTranslationApi(String inputText, String sourceLang, String targetLang) throws Exception {
		// Base URI
		RestAssured.baseURI = "https://13.203.149.17";

		// Build the JSON payload
		JSONObject payload = new JSONObject().put("controlConfig", new JSONObject().put("dataTracking", true))
				.put("config",
						new JSONObject().put("serviceId", "ai4bharat/indictrans--gpu-t4").put("language",
								new JSONObject().put("sourceLanguage", sourceLang).put("sourceScriptCode", "")
										.put("targetLanguage", targetLang).put("targetScriptCode", "")))
				.put("input", new JSONArray().put(new JSONObject().put("source", inputText)));

		// Send POST request
		return RestAssured.given().relaxedHTTPSValidation() // Bypass SSL issues due to IP
				.contentType(ContentType.JSON).accept(ContentType.JSON).header("x-auth-source", "API_KEY")
				.header("Authorization", "CE6rrAxAIFglquUYZJaVClTlx7FjhxVWGXLE6sOnxIkqK1UE6a9-ojnRpZ7GJYma")
				.body(payload.toString()).when().post("/services/inference/translation").then().extract().response();
	}

	public Response callTranslationApiForJson(String inputText, String sourceLang, String sourceScript,
			String targetLang, String targetScript) {
		RestAssured.baseURI = "https://13.203.149.17";

		JSONObject payload = new JSONObject().put("controlConfig", new JSONObject().put("dataTracking", true))
				.put("config",
						new JSONObject().put("serviceId", "ai4bharat/indictrans--gpu-t4").put("language",
								new JSONObject().put("sourceLanguage", sourceLang).put("sourceScriptCode", sourceScript)
										.put("targetLanguage", targetLang).put("targetScriptCode", targetScript)))
				.put("input", new JSONArray().put(new JSONObject().put("source", inputText)));

		return RestAssured.given().relaxedHTTPSValidation().contentType(ContentType.JSON).accept(ContentType.JSON)
				.header("x-auth-source", "API_KEY")
				.header("Authorization", "CE6rrAxAIFglquUYZJaVClTlx7FjhxVWGXLE6sOnxIkqK1UE6a9-ojnRpZ7GJYma")
				.body(payload.toString()).when().post("/services/inference/translation").then().extract().response();
	}

	public Response callAsrWithBase64(String base64Audio, String languageCode) {
		JSONObject config = new JSONObject().put("audioFormat", "wav").put("encoding", "base64")
				.put("samplingRate", 16000).put("serviceId", "ai4bharat/indictasr")
				.put("language", new JSONObject().put("sourceLanguage", languageCode).put("sourceScriptCode", ""))
				.put("preProcessors", new JSONArray()).put("postProcessors", new JSONArray())
				.put("transcriptionFormat", new JSONObject().put("value", "transcript")).put("bestTokenCount", 5);

		JSONObject requestBody = new JSONObject().put("controlConfig", new JSONObject().put("dataTracking", true))
				.put("config", config)
				.put("audio", new JSONArray().put(new JSONObject().put("audioContent", base64Audio)));

		return RestAssured.given().relaxedHTTPSValidation().contentType(ContentType.JSON).accept(ContentType.JSON)
				.header("x-auth-source", "API_KEY")
				.header("Authorization", "CE6rrAxAIFglquUYZJaVClTlx7FjhxVWGXLE6sOnxIkqK1UE6a9-ojnRpZ7GJYma")
				.body(requestBody.toString()).when().post("https://13.203.149.17/services/inference/asr").then()
				.extract().response();
	}

	public Response callAsrApiForJson(String sourceLang, String sourceScript) throws Exception {

		String base64Audio = encodeFileToBase64(audioFilePath);

		JSONObject payload = new JSONObject().put("controlConfig", new JSONObject().put("dataTracking", true))
				.put("config",
						new JSONObject().put("serviceId", "ai4bharat/indictasr").put("audioFormat", "wav")
								.put("encoding", "string").put("samplingRate", 0)
								.put("language",
										new JSONObject().put("sourceLanguage", sourceLang).put("sourceScriptCode",
												sourceScript))
								.put("preProcessors", new JSONArray().put("string"))
								.put("postProcessors", new JSONArray().put("string"))
								.put("transcriptionFormat", new JSONObject().put("value", "transcript"))
								.put("bestTokenCount", 0))
				.put("audio", new JSONArray().put(new JSONObject().put("audioContent", base64Audio)));

		return RestAssured.given().relaxedHTTPSValidation().contentType(ContentType.JSON).accept(ContentType.JSON)
				.header("x-auth-source", "API_KEY")
				.header("Authorization", "CE6rrAxAIFglquUYZJaVClTlx7FjhxVWGXLE6sOnxIkqK1UE6a9-ojnRpZ7GJYma")
				.body(payload.toString()).when().post("https://13.203.149.17/services/inference/asr").then().extract()
				.response();
	}

	public String encodeFileToBase64(String originalFilePath) throws Exception {
		File originalFile = new File(originalFilePath);
		if (!originalFile.exists()) {
			throw new FileNotFoundException("File not found: " + originalFilePath);
		}

		// Detect OS
		String osName = System.getProperty("os.name").toLowerCase();
		boolean isWindows = osName.contains("win");

		// FFmpeg binary
		String ffmpegCmd = isWindows ? "C:\\ffmpeg\\bin\\ffmpeg.exe" : "ffmpeg";

		// ENV override
		String ffmpegEnvPath = System.getenv("FFMPEG_PATH");
		if (ffmpegEnvPath != null && !ffmpegEnvPath.isBlank()) {
			ffmpegCmd = ffmpegEnvPath;
		}

		// Output temp .wav file
		File tempWav = File.createTempFile("converted_", ".wav");

		// FFmpeg command
		ProcessBuilder pb = new ProcessBuilder(
				ffmpegCmd,
				"-y",
				"-loglevel", "quiet",         // <- key suppression flag
				"-i", originalFile.getAbsolutePath(),
				"-ar", "16000",
				"-ac", "1",
				"-sample_fmt", "s16",
				tempWav.getAbsolutePath()
		);

		// Redirect output/error to OS null
		File nullSink = isWindows ? new File("NUL") : new File("/dev/null");
		pb.redirectOutput(nullSink);
		pb.redirectError(nullSink);

		Process process;
		try {
			process = pb.start();
		} catch (IOException e) {
			throw new IOException("Failed to start FFmpeg. Tried: " + ffmpegCmd, e);
		}

		int exitCode = process.waitFor();
		if (exitCode != 0 || !tempWav.exists() || tempWav.length() == 0) {
			tempWav.delete();  // cleanup on failure
			throw new RuntimeException("FFmpeg failed or produced no output (exit code: " + exitCode + ")");
		}

		// Convert to base64
		String base64;
		try {
			byte[] audioBytes = Files.readAllBytes(tempWav.toPath());
			base64 = Base64.getEncoder().encodeToString(audioBytes);
		} finally {
			tempWav.delete(); // cleanup always
		}

		return base64;
	}
}
