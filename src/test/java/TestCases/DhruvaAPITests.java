package TestCases;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.json.JSONArray;
import org.json.JSONObject;
import org.testng.asserts.SoftAssert;

import io.restassured.response.Response;
import java.util.*;
import com.aventstack.extentreports.Status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.BufferedWriter;
import java.io.File;
import java.util.concurrent.atomic.AtomicInteger;

import LibraryFiles.APIHelper;

public class DhruvaAPITests extends A_BaseSuiteFile {
	APIHelper api = new APIHelper();

	private static final Map<String, String> langCodeMap = Map.ofEntries(Map.entry("Assamese", "as"),
			Map.entry("Bangla", "bn"), Map.entry("Boro", "brx"), Map.entry("Dogri", "doi"),
			Map.entry("Goan-Konkani", "gom"), Map.entry("Gujarati", "gu"), Map.entry("Hindi", "hi"),
			Map.entry("Kannada", "kn"), Map.entry("Kashmiri", "ks"), Map.entry("Maithili", "mai"),
			Map.entry("Malayalam", "ml"), Map.entry("Manipuri", "mni"), Map.entry("Marathi", "mr"),
			Map.entry("Nepali", "ne"), Map.entry("Oriya", "or"), Map.entry("Panjabi", "pa"),
			Map.entry("Sanskrit", "sa"), Map.entry("Santali", "sat"), Map.entry("Sindhi", "sd"),
			Map.entry("Tamil", "ta"), Map.entry("Telugu", "te"), Map.entry("Urdu", "ur"), Map.entry("English", "en"));

	private static final Map<String, String> languageTextMap = Map.ofEntries(Map.entry("en", "This is a test API"),
			Map.entry("hi", "यह एक परीक्षण एपीआई है"), Map.entry("bn", "এটি একটি পরীক্ষামূলক এপিআই।"),
			Map.entry("ta", "இது ஒரு சோதனை API"), Map.entry("te", "ఇది ఒక పరీక్ష API"),
			Map.entry("gu", "આ એક પરીક્ષણ એપીઆઇ છે"), Map.entry("ml", "ഇത് ഒരു ടെസ്റ്റ് API ആണ്"),
			Map.entry("mr", "हा एक चाचणी API आहे"), Map.entry("kn", "ಇದು ಟೆಸ್ಟ್ API ಆಗಿದೆ"),
			Map.entry("pa", "ਇਹ ਇੱਕ ਟੈਸਟ ਏਪੀਆਈ ਹੈ"), Map.entry("or", "ଏହା ଗୋଟିଏ ପରୀକ୍ଷଣ API ଅଟେ"),
			Map.entry("ur", "یہ ایک ٹیسٹ API ہے"), Map.entry("ne", "यो परीक्षण एपीआई हो"),
			Map.entry("sd", "اهو هڪ ٽيسٽ API آهي"), Map.entry("ks", "یہ ایک ٹیسٹ API ہے"),
			Map.entry("mai", "ई एक परीक्षण एपीआई अछि"), Map.entry("sa", "एषः परीक्षणः API अस्ति"),
			Map.entry("as", "এইটো এটা পৰীক্ষামূলক API"), Map.entry("brx", "गोजै सायनो थुं API"),
			Map.entry("gom", "हांव एक टेस्ट API आसा"), Map.entry("mni", "ꯑꯁꯤ ꯍꯟꯗ ꯑꯁꯤ ꯇꯦꯁꯇ ꯑꯄꯤꯑꯤ"),
			Map.entry("doi", "इक टैस्ट API ऐ"), Map.entry("sat", "ᱚᱠᱷᱟ ᱵᱟᱝ API ᱠᱟᱱᱟ"));

	private static final List<String> languageNames = new ArrayList<>(langCodeMap.keySet());

	public void RunTTSAPIAndCheckResponse() throws Exception {
		SoftAssert softAssert = new SoftAssert();
		for (String lang : languageNames) {
			String langCode = langCodeMap.get(lang);
			logger.log(Status.INFO, "[TTS] Testing language: " + lang);
			System.out.println("[TTS] Testing language: " + lang);
			try {
				Response response = api.callTtsApi("how are you?", langCode, "male");
				int status = response.statusCode();
                logger.log(Status.INFO, "Status Code: " + status);
                System.out.println("Status Code: " + status);
//                logger.log(Status.INFO, "Response: " + response.asPrettyString());

				softAssert.assertEquals(status, 200, lang + " - TTS API failed");
				System.out.println(lang + " - TTS API failed");
				softAssert.assertTrue(response.asString().contains("audioContent"), lang + " - Missing audio content - ");
				System.out.println(lang + " - Missing audio content - ");

				if (status == 200)
				{
					logger.log(Status.PASS, "TTS for Language " + lang + " passed with code 200");
					System.out.println("TTS for Language " + lang + " passed with code 200");
				}
				else
				{
					logger.log(Status.FAIL, "TTS for Language " + lang + " failed with code " + status + " and Response:\n" + response.asPrettyString());
					System.out.println("TTS for Language " + lang + " failed with code " + status + " and Response:\n" + response.asPrettyString());
				}
			} catch (Exception e) {
				logger.log(Status.FAIL, lang + " - TTS API exception: " + e.getMessage());
				System.out.println(lang + " - TTS API exception: " + e.getMessage());
				softAssert.fail(lang + " - TTS Exception: " + e.getMessage());
			}
		}

		softAssert.assertAll();
	}

	public void RunTranslationAPIAndCheckResponse() throws Exception {
		SoftAssert softAssert = new SoftAssert();
		for (String sourceLang : languageNames) {
			for (String targetLang : languageNames) {
				if (sourceLang.equals(targetLang))
					continue;

				String sourceCode = langCodeMap.get(sourceLang);
				String targetCode = langCodeMap.get(targetLang);
				String inputText = languageTextMap.getOrDefault(sourceCode, "This is a test API");

				logger.log(Status.INFO, "[Translation] Testing: " + sourceLang + " → " + targetLang);

				try {
					Response response = api.callTranslationApi(inputText, sourceCode, targetCode);
					int status = response.statusCode();

					// logger.log(Status.INFO, "Status Code: " + status);
					// logger.log(Status.INFO, "Response: " + response.asPrettyString());

					softAssert.assertEquals(status, 200, sourceLang + "→" + targetLang + " - Translation API failed");
					softAssert.assertTrue(response.asString().contains("target"),
							sourceLang + "→" + targetLang + " - Missing translation");

					if (status == 200)
						logger.log(Status.PASS, "Translation for Source Language " + sourceLang
								+ " and Target Language " + targetLang + " passed with code 200");
					else
						logger.log(Status.FAIL,
								"Translation for Source Language " + sourceLang + " and Target Language " + targetLang
										+ " failed with code " + status + " and Response:\n"
										+ response.asPrettyString());

				} catch (Exception e) {
					logger.log(Status.FAIL, sourceLang + "→" + targetLang + " - Exception: " + e.getMessage());
					softAssert.fail(sourceLang + "→" + targetLang + " - Exception: " + e.getMessage());
				}
			}
		}
	}

	public void RunASRAPIAndCheckResponse() throws Exception {
		SoftAssert softAssert = new SoftAssert();

		Path Recpath = Paths.get(System.getProperty("user.dir"), "TestData", "Recording.wav");
		String filePath = Recpath.toString();

		for (String lang : languageNames) {
			String langCode = langCodeMap.get(lang);
			logger.log(Status.INFO, "[ASR] Testing language: " + lang);

			try {
				String base64 = api.encodeFileToBase64(filePath.toString());

				System.out.println(lang + " - " + langCode);
				
				Response response = api.callAsrWithBase64(base64, langCode);
				int status = response.statusCode();

//                logger.log(Status.INFO, "Status Code: " + status);
//                logger.log(Status.INFO, "Response: " + response.asPrettyString());

				softAssert.assertEquals(status, 200, lang + " - ASR API failed");
				softAssert.assertTrue(response.asString().contains("transcript"), lang + " - Missing transcript");

				if (status == 200)
					logger.log(Status.PASS, "ASR for Language " + lang + " passed with code 200");
				else
					logger.log(Status.FAIL, "ASR for Language " + lang + " failed with code " + status
							+ " and Response:\n" + response.asPrettyString());

			} catch (Exception e) {
				logger.log(Status.FAIL, lang + " - ASR API exception: " + e.getMessage());
				softAssert.fail(lang + " - ASR Exception: " + e.getMessage());
			}
		}

		softAssert.assertAll();
	}

	public void runTranslationLanguageTestsFromJSON() throws Exception {
	    String jsonPath = "languages.json";
	    String logFileName = "translation_test_log.txt";

	    ObjectMapper mapper = new ObjectMapper();
	    JsonNode root = mapper.readTree(new File(jsonPath));

	    int total = root.size();
	    APIHelper api = new APIHelper();
	    List<ObjectNode> successfulTranslations = new ArrayList<>();

	    // Prepare log writer (try-with-resources ensures it's closed)
	    try (BufferedWriter logWriter = Files.newBufferedWriter(Paths.get(logFileName), StandardCharsets.UTF_8)) {

	        logWriter.write("====================================\n");
	        logWriter.write("Total translation pairs to test: " + total + "\n");
	        logWriter.write("====================================\n");

	        AtomicInteger count = new AtomicInteger(1);

	        for (JsonNode pair : root) {
	            String sourceLang = pair.path("sourceLanguage").asText();
	            String sourceScript = pair.path("sourceScriptCode").asText();
	            String targetLang = pair.path("targetLanguage").asText();
	            String targetScript = pair.path("targetScriptCode").asText();

	            int index = count.getAndIncrement();
	            String prefix = index + ". Testing " + sourceLang + "-" + sourceScript + " -> " + targetLang + "-" + targetScript + ": ";

	            System.out.print(prefix);
	            logWriter.write(prefix);

	            try {
	                Response response = api.callTranslationApiForJson("This is a test", sourceLang, sourceScript, targetLang, targetScript);
	                int statusCode = response.getStatusCode();
	                String responseBody = response.asPrettyString();

	                boolean hasOutput = response.jsonPath().getList("output") != null
	                        && !response.jsonPath().getList("output").isEmpty();

	                if (statusCode == 200 && hasOutput) {
	                    System.out.printf("Success (Status %d)%n", statusCode);
	                    logWriter.write("Success (Status " + statusCode + ")\n");

	                    ObjectNode success = mapper.createObjectNode();
	                    success.put("sourceLanguage", sourceLang);
	                    success.put("sourceScriptCode", sourceScript);
	                    success.put("targetLanguage", targetLang);
	                    success.put("targetScriptCode", targetScript);
	                    successfulTranslations.add(success);
	                } else {
	                    System.out.printf("Failed (Status %d)%n", statusCode);
	                    logWriter.write("Failed (Status " + statusCode + ") - " + responseBody + "\n");
	                }

	            } catch (Exception e) {
	                System.out.println("Error: " + e.getMessage());
	                logWriter.write("Error: " + e.getMessage() + "\n");
	            }

	            logWriter.flush(); // ensures line is written even if test fails mid-way
	        }

	        // Write final successful list
	        logWriter.write("\nSuccessfully Tested Language-Script Pairs (Translation):\n");
	        if (!successfulTranslations.isEmpty()) {
	            String prettyJson = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(successfulTranslations);
	            logWriter.write(prettyJson);
	        } else {
	            logWriter.write("None\n");
	        }
	    }

	    System.out.println("\nTranslation test completed. Log written to: " + logFileName);
	}

	public void runTTSLanguageTestsFromJSON() throws Exception {
		String jsonPath = "languages.json";
		ObjectMapper mapper = new ObjectMapper();
		JsonNode root = mapper.readTree(new File(jsonPath));

		Set<String> uniqueSourceLangPairs = new HashSet<>();
		List<JSONObject> successfulLanguages = new ArrayList<>();
		APIHelper api = new APIHelper();

		// Extract unique TTS input language-script combinations
		for (JsonNode node : root) {
			if (!node.hasNonNull("targetLanguage") || !node.hasNonNull("targetScriptCode")) {
				continue;
			}
			String lang = node.path("targetLanguage").asText().trim();
			String script = node.path("targetScriptCode").asText().trim();

			if (!lang.isEmpty() && !script.isEmpty()) {
				uniqueSourceLangPairs.add(lang + "||" + script);
			}
		}

		System.out.println("====================================");
		System.out.println("Total TTS language-script to test: " + uniqueSourceLangPairs.size());
		System.out.println("====================================");

		AtomicInteger count = new AtomicInteger(1);

		for (String entry : uniqueSourceLangPairs) {
			String[] parts = entry.split("\\|\\|");
			String sourceLang = parts[0];
			String sourceScript = parts[1];

			int index = count.getAndIncrement();
			System.out.printf("%d. Testing %s-%s: ", index, sourceLang, sourceScript);

			try {
				Response response = api.callTtsApiForJson("this is a test", sourceLang, sourceScript);
				int statusCode = response.getStatusCode();

				if (statusCode == 200) {
					System.out.printf("Success (Status %d)%n", statusCode);

					// Track successful pair
					JSONObject successObj = new JSONObject().put("sourceLanguage", sourceLang).put("sourceScriptCode",
							sourceScript);
					successfulLanguages.add(successObj);

				} else {
					System.out.printf("Failed (Status %d) - %s%n", statusCode, response.asString());
				}

			} catch (Exception e) {
				System.out.println("Error: " + e.getMessage());
			}
		}

		// Print final successful language-script combinations in JSON
		System.out.println("\nSuccessfully Tested Language-Script Pairs for TTS Model:");
		JSONArray finalSuccessArray = new JSONArray(successfulLanguages);
		System.out.println(finalSuccessArray.toString(2)); // Pretty print with indentation
	}

	public void runASRLanguageTestsFromJSON() throws Exception {
		String jsonPath = "languages.json";
		ObjectMapper mapper = new ObjectMapper();
		JsonNode root = mapper.readTree(new File(jsonPath));

		Set<String> uniqueSourceLangPairs = new HashSet<>();
		List<JSONObject> successfulLanguages = new ArrayList<>();
		APIHelper api = new APIHelper();

		// Extract unique (targetLanguage + targetScript) pairs for ASR
		for (JsonNode node : root) {
			if (!node.hasNonNull("targetLanguage") || !node.hasNonNull("targetScriptCode")) {
				continue;
			}
			String lang = node.path("targetLanguage").asText().trim();
			String script = node.path("targetScriptCode").asText().trim();

			if (!lang.isEmpty() && !script.isEmpty()) {
				uniqueSourceLangPairs.add(lang + "||" + script);
			}
		}

		System.out.println("====================================");
		System.out.println("Total ASR language-script to test: " + uniqueSourceLangPairs.size());
		System.out.println("====================================");

		AtomicInteger count = new AtomicInteger(1);

		for (String entry : uniqueSourceLangPairs) {
			String[] parts = entry.split("\\|\\|");
			String sourceLang = parts[0];
			String sourceScript = parts[1];

			int index = count.getAndIncrement();
			System.out.printf("%d. Testing %s-%s: ", index, sourceLang, sourceScript);

			try {
				Response response = api.callAsrApiForJson(sourceLang, sourceScript); // callAsrApiForJson must be
																						// defined
				int statusCode = response.getStatusCode();

				if (statusCode == 200) {
					System.out.printf("Success (Status %d)%n", statusCode);

					JSONObject successObj = new JSONObject().put("sourceLanguage", sourceLang).put("sourceScriptCode",
							sourceScript);
					successfulLanguages.add(successObj);
				} else {
					System.out.printf("Failed (Status %d) - %s%n", statusCode, response.asString());
				}

			} catch (Exception e) {
				System.out.println("Error: " + e.getMessage());
			}
		}

		// Print successful results as JSON
		System.out.println("\nSuccessfully Tested Language-Script Pairs (ASR):");
		JSONArray finalSuccessArray = new JSONArray(successfulLanguages);
		System.out.println(finalSuccessArray.toString(2));
	}
}
