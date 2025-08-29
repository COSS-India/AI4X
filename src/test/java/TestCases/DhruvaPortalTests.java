package TestCases;

import java.nio.file.Path;
import java.nio.file.Paths;

import org.openqa.selenium.TimeoutException;
import org.testng.asserts.SoftAssert;

import com.aventstack.extentreports.Status;

import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import ObjectRepository.DhruvaPortalPage;

public class DhruvaPortalTests extends A_BaseSuiteFile {
	Path path = Paths.get(System.getProperty("user.dir"), "TestData", "TestData.properties");
	String dataFilePath = path.toString();

	public void OpenDhruvaPortalAndTestASRForAllLanguages() throws Exception {
		SoftAssert softAssert = new SoftAssert();

		System.out.println("\nLanded on Dhruva Portal\n");
		logger.log(Status.INFO, "Landed on Dhruva Portal");
		DhruvaPortalPage dhruva = new DhruvaPortalPage(driver);

		System.out.println("Validating whether Page Header is Displayed\n");
		logger.log(Status.INFO, "Validating whether Page Header is Displayed");
		softAssert.assertEquals(dhruva.getPageHeader(), "Login into Dhruva", "[The Page Header should be Visible] - ");
		softAssert.assertTrue(dhruva.isPageHeaderClickable(), "[The Page Header should be Enabled and Clickable] - ");

//		System.out.println("Clicking on the Profile Button\n");
//		logger.log(Status.INFO, "Clicking on the Profile Button");
//		dhruva.clickOnProfileBtn();
//		System.out.println("Clicking on the Logout Button\n");
//		logger.log(Status.INFO, "Clicking on the Logout Button");
//		dhruva.clickOnLogoutBtn();

		LoginToApplication();

		System.out.println("Clicking on the third 'View' button\n");
		logger.log(Status.INFO, "Clicking on the third 'View' button");
		dhruva.clickOnThirdViewBtn();
		Thread.sleep(1000);

		dhruva.waitUntilTryItOutTxtVisible();
		Thread.sleep(1000);

		System.out.println("Validating whether landed on the correct page for microphone test\n");
		logger.log(Status.INFO, "Validating whether landed on the correct page for microphone test");
		softAssert.assertEquals(dhruva.getTryItOutTxt(), "Try it out here!",
				"[The 'Try it out here!' text should be Visible] - ");

		ScrollDownToBottomOfWebpage();

		System.out.println("Validating that the translated text is correct or not\n");
		logger.log(Status.INFO, "Validating that the translated text is correct or not");

		String[] lang = new String[23];

		for (int i = 0; i < lang.length; i++) {
			lang[i] = dhruva.getLanguage(i);
		}

		int n = 0;
		while (n < lang.length) {
			ScrollUpToGivenPixels(250);
			System.out.println("Selecting '" + lang[n] + "' from the list of languages to translate the speech to\n");
			logger.log(Status.INFO,
					"Selecting '" + lang[n] + "' from the list of languages to translate the speech to");
			dhruva.selectLanguage(lang[n]);
			Thread.sleep(1000);
			ScrollDownToBottomOfWebpage();

			System.out.println("Clicking on the 'Start Recording' Button\n");
			logger.log(Status.INFO, "Clicking on the 'Start Recording' Button");
			dhruva.clickOnStartRecBtn();

			System.out.println("Waiting for the Speech Input to be listened...\n");
			logger.log(Status.INFO, "Waiting for the Speech Input to be listened...");
			Thread.sleep(4000);

			System.out.println("Clicking on the 'Stop Recording' Button\n");
			logger.log(Status.INFO, "Clicking on the 'Stop Recording' Button");
			dhruva.clickOnStopRecBtn();

			String result = dhruva.waitUntilElementVisibleOrASRFail();

			if ("ASR_FAILED".equals(result)) {
				System.out.println("ASR failure detected for language '" + lang[n] + "', skipping this language...\n");
				logger.log(Status.FAIL, "ASR failure detected for language " + lang[n]);
			} else if ("SUCCESS".equals(result)) {
				String response = dhruva.getResponse();

				System.out.println("The ASR translated text is: " + response);
				logger.log(Status.INFO, "The ASR translated text is: " + response);

				softAssert.assertTrue(dhruva.isResponseDisplayed(),
						"[The Response should be Displayed for Language " + lang[n] + "] - ");

				logger.log(Status.PASS, "The ASR translation for language '" + lang[n] + "' is passed");
			} else {
				System.out.println("Timeout waiting for result for language '" + lang[n] + "'\n");
				logger.log(Status.FAIL, "Timeout waiting for result for language " + lang[n]);
			}

			Thread.sleep(1000);
			n++;
		}

		softAssert.assertAll();
	}

	public void OpenDhruvaPortalAndTestTTSForAllLanguages() throws Exception {
		SoftAssert softAssert = new SoftAssert();

		System.out.println("\nLanded on Dhruva Portal\n");
		logger.log(Status.INFO, "Landed on Dhruva Portal");
		DhruvaPortalPage dhruva = new DhruvaPortalPage(driver);

		System.out.println("Validating whether Page Header is Displayed\n");
		logger.log(Status.INFO, "Validating whether Page Header is Displayed");
		softAssert.assertEquals(dhruva.getPageHeader(), "Login into Dhruva", "[The Page Header should be Visible] - ");
		softAssert.assertTrue(dhruva.isPageHeaderClickable(), "[The Page Header should be Enabled and Clickable] - ");

//		System.out.println("Clicking on the Profile Button\n");
//		logger.log(Status.INFO, "Clicking on the Profile Button");
//		dhruva.clickOnProfileBtn();
//		System.out.println("Clicking on the Logout Button\n");
//		logger.log(Status.INFO, "Clicking on the Logout Button");
//		dhruva.clickOnLogoutBtn();

		LoginToApplication();

		System.out.println("Clicking on the second 'View' button\n");
		logger.log(Status.INFO, "Clicking on the second 'View' button");
		dhruva.clickOnSecondViewBtn();
		Thread.sleep(1000);

		dhruva.waitUntilTryItOutTxtVisible();
		Thread.sleep(1000);

		System.out.println("Validating whether landed on the correct page for TTS test\n");
		logger.log(Status.INFO, "Validating whether landed on the correct page for TTS test");
		softAssert.assertEquals(dhruva.getTryItOutTxt(), "Try it out here!",
				"[The 'Try it out here!' text should be Visible] - ");

		ScrollDownToBottomOfWebpage();

		String[] languages = { "Assamese", "Bangla", "Boro", "Dogri", "Goan-Konkani", "Gujarati", "Hindi", "Kannada",
				"Kashmiri", "Maithili", "Malayalam", "Manipuri", "Marathi", "Nepali", "Oriya", "Panjabi", "Sanskrit",
				"Santali", "Sindhi", "Tamil", "Telugu", "Urdu", "English" };

		for (int i = 0; i < languages.length; i++) {
			dhruva.selectTTsLanguage(languages[i]);

			ScrollDownToBottomOfWebpage();
			System.out.println("Starting audio validation for '" + languages[i] + "' language...");
			logger.log(Status.INFO, "Starting audio validation for '" + languages[i] + "' language");

			String inputText = dhruva.getInputTextForLanguage(languages[i]);
			dhruva.InputTextForTTS(inputText);
			dhruva.clickOnTextSubmitBtn();

			try {
				String result = dhruva.waitUntilElementVisibleOrTTSFail();

				if ("FAILED".equals(result)) {
					System.out.println(
							"TTS failure detected for language '" + languages[i] + "', skipping this language...\n");
					logger.log(Status.WARNING, "TTS failure detected for language " + languages[i]);
				} else if ("SUCCESS".equals(result)) {

					if (languages[i] == null) {
						System.out.println("Unsupported or unrecognized language code for: " + languages[i]
								+ ", skipping this language...");
						logger.log(Status.WARNING, "Unsupported language code for: " + languages[i]);
						continue;
					}

					boolean audioMatch = dhruva.validateTTSOutput(inputText, languages[i]);
					softAssert.assertTrue(audioMatch, "[The input text '" + inputText
							+ "' must match with the audio for the language '" + languages[i] + "'] - ");
					logger.log(Status.INFO, "TTS audio validation " + (audioMatch ? "PASSED" : "FAILED"));
				} else {
					System.out.println(
							"TTS failure detected for language '" + languages[i] + "', skipping this language...\n");
					logger.log(Status.WARNING, "TTS failure detected for language " + languages[i]);
				}
			} catch (TimeoutException e) {
				System.out.println(
						"Timeout while waiting for TTS response for language '" + languages[i] + "', skipping...\n");
				logger.log(Status.WARNING, "Timeout occurred for language " + languages[i]);
			} catch (Exception e) {
				System.out.println("Unexpected error for language '" + languages[i] + "': " + e.getMessage());
				logger.log(Status.FAIL,
						"Unexpected error during TTS validation for language " + languages[i] + ": " + e.getMessage());
			}

			ScrollUpToGivenPixels(300);
		}
		softAssert.assertAll();
	}

	public void OpenDhruvaPortalAndTestTranslationForAllLanguages() throws Exception {
		SoftAssert softAssert = new SoftAssert();

		System.out.println("\nLanded on Dhruva Portal\n");
		logger.log(Status.INFO, "Landed on Dhruva Portal");
		DhruvaPortalPage dhruva = new DhruvaPortalPage(driver);

		System.out.println("Validating whether Page Header is Displayed\n");
		logger.log(Status.INFO, "Validating whether Page Header is Displayed");
		softAssert.assertEquals(dhruva.getPageHeader(), "Login into Dhruva", "[The Page Header should be Visible] - ");
		softAssert.assertTrue(dhruva.isPageHeaderClickable(), "[The Page Header should be Enabled and Clickable] - ");

//		System.out.println("Clicking on the Profile Button\n");
//		logger.log(Status.INFO, "Clicking on the Profile Button");
//		dhruva.clickOnProfileBtn();
//		System.out.println("Clicking on the Logout Button\n");
//		logger.log(Status.INFO, "Clicking on the Logout Button");
//		dhruva.clickOnLogoutBtn();

		LoginToApplication();

		System.out.println("Clicking on the second 'View' button\n");
		logger.log(Status.INFO, "Clicking on the second 'View' button");
		dhruva.clickOnFirstViewBtn();
		Thread.sleep(1000);

		dhruva.waitUntilTryItOutTxtVisible();
		Thread.sleep(1000);

		System.out.println("Validating whether landed on the correct page for Translation test\n");
		logger.log(Status.INFO, "Validating whether landed on the correct page for Translation test");
		softAssert.assertEquals(dhruva.getTryItOutTxt(), "Try it out here!",
				"[The 'Try it out here!' text should be Visible] - ");

		long overallStart = System.currentTimeMillis();

		List<String> dropdownOptions = dhruva.getAllLanguageDropdownOptions().stream().map(String::trim)
				.collect(Collectors.toList());

		Set<String> uniqueOptions = new HashSet<>();
		Set<String> duplicateOptions = new HashSet<>();

		for (String option : dropdownOptions) {
			if (!uniqueOptions.add(option)) {
				duplicateOptions.add(option);
			}
		}
		if (!duplicateOptions.isEmpty()) {
			logger.log(Status.WARNING, "Duplicate dropdown entries found: " + duplicateOptions);
		}

		Set<String> dropdownSet = new HashSet<>(dropdownOptions);
		int totalCombos = testInputsByLanguage.size() * (testInputsByLanguage.size() - 1);
		int currentCount = 0;

		Set<String> languagesMissingToEnglish = new HashSet<>();

		for (String sourceLang : testInputsByLanguage.keySet()) {
			boolean hasToEnglish = false;

			for (String targetLang : testInputsByLanguage.keySet()) {
				if (sourceLang.equals(targetLang))
					continue;

				String combo = sourceLang + " -> " + targetLang;

				if (!dropdownSet.contains(combo)) {
					logger.log(Status.WARNING, "Missing dropdown entry: " + combo);
					softAssert.fail("Missing translation direction: " + combo);
					continue;
				}

				if (targetLang.equals("English")) {
					hasToEnglish = true;
				}

				currentCount++;
				String inputText = testInputsByLanguage.get(sourceLang);

				logger.log(Status.INFO, "Translation " + currentCount + " of " + totalCombos);
				logger.log(Status.INFO, "Source Language: " + sourceLang);
				logger.log(Status.INFO, "Target Language: " + targetLang);
				logger.log(Status.INFO, "Input Text: " + inputText);

				try {
					dhruva.selectLangComboFromDropdown(combo);
					dhruva.InputTranslationText(inputText);

					long startTime = System.nanoTime();
					dhruva.clickOnTranslateBtn();
					String output = dhruva.getTranslatedOutput(combo);
					long responseTimeMs = (System.nanoTime() - startTime) / 1_000_000;

					logger.log(Status.INFO, "Output Text: " + output);
					logger.log(Status.INFO, "Response Time: " + responseTimeMs + " ms");

					if (output.isEmpty()) {
						logger.log(Status.FAIL, "Empty output for combo: " + combo);
					}

				} catch (Exception e) {
					logger.log(Status.FAIL, "Exception for combo [" + combo + "]: " + e.getMessage());
					softAssert.fail("Translation failed for: " + combo + " due to: " + e.getMessage());
				}
			}

			if (!hasToEnglish) {
				logger.log(Status.FAIL, "No translation found from [" + sourceLang + "] to English.");
				languagesMissingToEnglish.add(sourceLang);
			}
		}

		long duration = System.currentTimeMillis() - overallStart;
		logger.log(Status.INFO, "Translation Test Completed: " + currentCount + " combinations tested.");
		logger.log(Status.INFO, "Total execution time: " + duration + " ms");

		if (!languagesMissingToEnglish.isEmpty()) {
			logger.log(Status.WARNING, "Languages missing translation to English: " + languagesMissingToEnglish);
		}

		softAssert.assertAll();
	}

	private static final Map<String, String> testInputsByLanguage = Map.ofEntries(
			Map.entry("Assamese", "এইটো এটা পৰীক্ষা বাক্য।"), Map.entry("Bangla", "এটি একটি পরীক্ষামূলক বাক্য।"),
			Map.entry("Boro", "बिबार दांगाओ ऑनसर।"), Map.entry("Dogri", "इह इक टैस्ट वाक्य है।"),
			Map.entry("Goan-Konkani", "हें एक परीक्षण वाक्य आसा."), Map.entry("Gujarati", "આ એક પરીક્ષણ વાક્ય છે."),
			Map.entry("Hindi", "यह एक परीक्षण वाक्य है।"), Map.entry("Kannada", "ಇದು ಪರೀಕ್ಷಾ ವಾಕ್ಯವಾಗಿದೆ."),
			Map.entry("Kashmiri", "یەہ ایک تجرباتی جملہ ہے۔"), Map.entry("Maithili", "ई एक परीक्षण वाक्य अछि।"),
			Map.entry("Malayalam", "ഇത് ഒരു പരീക്ഷണ വാക്യം ആണ്."), Map.entry("Manipuri", "ꯑꯃꯨ ꯇꯦꯡꯕꯥ ꯋꯥꯛꯌꯦꯝ ꯑꯃꯁꯤ."),
			Map.entry("Marathi", "हे एक चाचणी वाक्य आहे."), Map.entry("Nepali", "यो एउटा परीक्षण वाक्य हो।"),
			Map.entry("Oriya", "ଏହା ଏକ ପରୀକ୍ଷା ବାକ୍ୟ ଅଟେ।"), Map.entry("Panjabi", "ਇਹ ਇੱਕ ਟੈਸਟ ਵਾਕ ਹੈ।"),
			Map.entry("Sanskrit", "एषः एकः परीक्षणवाक्यम् अस्ति।"), Map.entry("Santali", "ᱮᱱᱟ ᱪᱚᱛ ᱰᱟᱨᱮ ᱥᱮᱱᱨᱮ।"),
			Map.entry("Sindhi", "ھيءُ ھڪ آزمائشي جملو آھي."), Map.entry("Tamil", "இது ஒரு சோதனை வாசகம்."),
			Map.entry("Telugu", "ఇది ఒక పరీక్ష వాక్యం."), Map.entry("Urdu", "یہ ایک تجرباتی جملہ ہے۔"),
			Map.entry("English", "This is a test sentence."));

	public void OpenDhruvaPortalAndTestS2SForAllLanguages() throws Exception {
		SoftAssert softAssert = new SoftAssert();

		System.out.println("\nLanded on Dhruva Portal\n");
		logger.log(Status.INFO, "Landed on Dhruva Portal");
		DhruvaPortalPage dhruva = new DhruvaPortalPage(driver);

		System.out.println("Validating whether Page Header is Displayed\n");
		logger.log(Status.INFO, "Validating whether Page Header is Displayed");
		softAssert.assertEquals(dhruva.getPageHeader(), "Login into Dhruva", "[The Page Header should be Visible] - ");
		softAssert.assertTrue(dhruva.isPageHeaderClickable(), "[The Page Header should be Enabled and Clickable] - ");

		LoginToApplication();

		dhruva.clickOnPipelineBtn();
		dhruva.waitUntilPipelineHeaderVisible();
		Thread.sleep(1000);

		Path audioPath = Paths.get(System.getProperty("user.dir"), "TestData", "Recording.wav");
		String audioFilePath = audioPath.toAbsolutePath().toString();

		String[] languages = { "Assamese", "Bangla", "Boro", "Dogri", "Goan-Konkani", "Gujarati", "Hindi", "Kannada",
				"Kashmiri", "Maithili", "Malayalam", "Manipuri", "Marathi", "Nepali", "Oriya", "Panjabi", "Sanskrit",
				"Santali", "Sindhi", "Tamil", "Telugu", "Urdu", "English" };

		for (String sourceLang : languages) {
			for (String targetLang : languages) {

				// Skip same source & target (if not needed)
				if (sourceLang.equals(targetLang))
					continue;

				try 
				{
					dhruva.selectSourceLanguages(sourceLang);
					dhruva.selectTargetLanguages(targetLang);
					dhruva.uploadAudioFile(audioFilePath);

					String result = dhruva.waitUntilElementVisibleOrS2SFail();

					switch (result) {
					case "FAILED":
						System.out.println("S2S failure detected for Source: " + sourceLang + " → Target: " + targetLang);
						logger.log(Status.WARNING, "S2S failure detected for Source: " + sourceLang + " → Target: " + targetLang);
						continue;

					case "SUCCESS":
						System.out.println("S2S passed for Source: " + sourceLang + " → Target: " + targetLang);
						logger.log(Status.PASS, "S2S passed for Source: " + sourceLang + " → Target: " + targetLang);
						ScrollDownToGivenPixels(500);
						break;

					default:
						System.out.println("Unknown status for Source: " + sourceLang + " → Target: " + targetLang);
						logger.log(Status.WARNING, "Unknown status for Source: " + sourceLang + " → Target: " + targetLang);
						continue;
					}

					softAssert.assertTrue(dhruva.isSourceTextVisible(), "The source text should be visible for " + sourceLang);
					softAssert.assertTrue(dhruva.isTargetTextVisible(), "The target text should be visible for " + targetLang);

					ScrollUpToGivenPixels(500);

				} catch (TimeoutException e) {
					System.out.println("Timeout for Source: " + sourceLang + " → Target: " + targetLang);
					logger.log(Status.WARNING, "Timeout for Source: " + sourceLang + " → Target: " + targetLang);
				} catch (Exception e) {
					System.out.println("Unexpected error for Source: " + sourceLang + " → Target: " + targetLang + " | Error: " + e.getMessage());
					logger.log(Status.FAIL, "Unexpected error for Source: " + sourceLang + " → Target: " + targetLang + " | Error: " + e.getMessage());
				}
			}
		}

		softAssert.assertAll();
	}
}
