package ObjectRepository;

import java.io.BufferedReader;
import java.io.File;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Optional;
import java.util.stream.Collectors;
import java.io.InputStreamReader;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.Keys;
import org.openqa.selenium.StaleElementReferenceException;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.SearchContext;

// Apache Commons
import org.apache.commons.io.FileUtils;

import java.nio.charset.StandardCharsets;
import java.nio.file.Paths;
import java.util.Base64;

import com.aventstack.extentreports.Status;

import LibraryFiles.ReusableLibraryFile;

public class DhruvaPortalPage  extends ReusableLibraryFile
{
	By pageHeader = By.xpath("//h2[contains(text(), 'Login into Dhruva')]");
	By pagesubHeader = By.xpath("//h2[contains(text(), 'Language Settings')]/parent::div/following-sibling::div/h2");
	By firstViewBtn = By.xpath("//table/tbody/tr[1]/td[5]//button");
	By secondViewBtn = By.xpath("//table/tbody/tr[2]/td[5]//button");
	By thirdViewBtn = By.xpath("//table/tbody/tr[3]/td[5]//button");
	By tryItOutTxt = By.xpath("//h2[contains(text(), 'Try it out here!')]");
	By StartRecBtn = By.xpath("//button[@title='Start Recording']");
	By StopRecBtn = By.xpath("//button[text()='Stop Recording']");
	By WordCountTxt = By.xpath("//dt[contains(text(), 'Word Count')]");
	By LanguageSelection = By.xpath("//p[contains(text(), 'Select Language')]/following-sibling::div/select");
	public By Response = By.xpath("//textarea");
	By ProfileBtn = By.xpath("//p[contains(text(), 'Admin')]/ancestor::button");
	By LogoutBtn = By.xpath("//button[contains(text(), 'Logout')]");
	By Audio = By.xpath("//button[contains(text(), 'Give us feedback!')]/parent::div/audio");
	
	By TTSLanguageSelect = By.xpath("//p[contains(text(), 'Select Language')]/following-sibling::div/select");
	By TextSubmitBtn = By.xpath("//textarea/parent::div/following-sibling::div/button");
	
	By TranslationSelect = By.xpath("//p[contains(text(), 'Languages:')]/following-sibling::div/select");
	By TranslationInputBox = By.xpath("//textarea[contains(@placeholder, 'Type your text here to translate')]");
	By TranslationOutputBox = By.xpath("//textarea[contains(@placeholder, 'View Translation Here')]");
	By TranslateBtn = By.xpath("//button[contains(text(), 'Translate')]");
	
	By PipelineBtn = By.xpath("//a[@href='/pipeline']/button");
	By PipelineSource = By.xpath("//p[contains(text(), 'Source')]/following-sibling::div/select");
	By PipelineTarget = By.xpath("//p[contains(text(), 'Target')]/following-sibling::div/select");
	By PipelineHeader = By.xpath("//h2[contains(text(), 'Pipeline (Speech2Speech)')]");
	By PipelineChooseFile = By.xpath("//label[contains(text(), 'Choose file')]");
	By PipelineSourceTextarea = By.xpath("//textarea[1]");
	By PipelineTargetTextarea = By.xpath("//textarea[2]");
	
	By TextAudioChatTab = By.xpath("(//div[@role='tablist'])[1]/button[1]");
	By VoiceChatTab = By.xpath("(//div[@role='tablist'])[1]/button[2]");
	By MicStartBtn = By.xpath("//button[@title='Start Recording']");
	By MicStopBtn = By.xpath("//button[@title='Stop Recording']");
	By NoOfMsgs = By.xpath("//form[@class='css-0']/preceding-sibling::div/div/div");
	
	
	
	
	@SuppressWarnings("static-access")
	public DhruvaPortalPage(WebDriver driver) {
		this.driver = driver;
	}
	
	public String getPageHeader()
	{
		return driver.findElement(pageHeader).getText().trim();
	}
	
	public boolean isPageHeaderClickable() throws Exception
	{
		return IsElementClickable(pageHeader);
	}
	
	public void clickOnFirstViewBtn()
	{
		driver.findElement(firstViewBtn).click();
	}
	
	public void clickOnSecondViewBtn()
	{
		driver.findElement(secondViewBtn).click();
	}
	
	public void clickOnThirdViewBtn()
	{
		driver.findElement(thirdViewBtn).click();
	}
	
	public void waitUntilTryItOutTxtVisible()
	{
		waitUntillElementVisible(tryItOutTxt);
	}
	
	public String getTryItOutTxt()
	{
		return driver.findElement(tryItOutTxt).getText().trim();
	}
	
	public void clickOnStartRecBtn()
	{
		driver.findElement(StartRecBtn).click();
	}
	
	public void clickOnStopRecBtn()
	{
		driver.findElement(StopRecBtn).click();
	}
	
	public String waitUntilElementVisibleOrASRFail() 
	{
	    By element = WordCountTxt;
	    By textareaLocator = Response;

	    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(50));

	    return wait.until(driver -> {
	        try 
	        {
	            List<WebElement> wordCountElements = driver.findElements(element);
	            if (!wordCountElements.isEmpty() && wordCountElements.get(0).isDisplayed()) 
	            {
	                return "SUCCESS";
	            }

	            List<WebElement> textareas = driver.findElements(textareaLocator);
	            if (!textareas.isEmpty()) 
	            {
	                String text = textareas.get(0).getText();
	                if (text != null && text.contains("[ASR Failed]")) 
	                {
	                    return "ASR_FAILED";
	                }
	            }

	        } catch (Exception e) 
	        {}
	        
	        return null;
	    });
	}
	
	
	
	public void selectLanguage(String value)
	{
		SelectDropDownByVisibleText(LanguageSelection, value);
	}
	
	public String getResponse()
	{
		return driver.findElement(Response).getText().trim();
	}
	
	public boolean isResponseDisplayed()
	{
		return driver.findElement(Response).isDisplayed();
	}
	
	public void clickOnProfileBtn()
	{
		driver.findElement(ProfileBtn).click();
	}
	
	public void clickOnLogoutBtn()
	{
		driver.findElement(LogoutBtn).click();
	}
	
	
	
	
	
	public String getPageSubHeader()
	{
		return driver.findElement(pagesubHeader).getText().trim();
	}
	
	public String getTextAudioChatTab()
	{
		return driver.findElement(TextAudioChatTab).getText().trim();
	}
	
	public String getVoiceChatTab()
	{
		return driver.findElement(VoiceChatTab).getText().trim();
	}
	
	public boolean isTextAudioChatTabClickable() throws Exception
	{
		return IsElementClickable(TextAudioChatTab);
	}
	
	public boolean isVoiceChatTabClickable() throws Exception
	{
		return IsElementClickable(VoiceChatTab);
	}
	
	public void clickOnStartMicBtn()
	{
		driver.findElement(MicStartBtn).click();
	}
	
	public void clickOnStopMicBtn()
	{
		driver.findElement(MicStopBtn).click();
	}
	
	public String getLastReply()
	{
		List<WebElement> rows = driver.findElements(NoOfMsgs);
        int totalNoOfMsgs = rows.size();
        
        By xpathBuild = By.xpath("//form[@class='css-0']/preceding-sibling::div/div/div["+(totalNoOfMsgs-1)+"]//p");
        return driver.findElement(xpathBuild).getText().trim();
	}

	public String getLanguage(int num) 
	{
	    String[] languages = 
	    {
	        "Assamese", "Bangla", "Boro", "Dogri", "Goan-Konkani", "Gujarati",
	        "Hindi", "Kannada", "Kashmiri", "Maithili", "Malayalam", "Manipuri",
	        "Marathi", "Nepali", "Oriya", "Panjabi", "Sanskrit", "Santali",
	        "Sindhi", "Tamil", "Telugu", "Urdu", "English"
	    };

	    if (num >= 0 && num < languages.length) 
	    {
	        return languages[num];
	    } else {
	        return "Unknown";
	    }
	}

	private static final Map<String, String> TRANSLATIONS = Map.ofEntries(
	        Map.entry("assamese", "হেল্ল' ৱৰ্ল্ড"),
	        Map.entry("bangla", "হ্যালো ওয়ার্ল্ড"),
	        Map.entry("boro", "हल्लो वर्ल्ड"),
	        Map.entry("dogri", "हैलो वर्ल्ड"),
	        Map.entry("goan-konkani", "हेलो वर्ल्ड"),
	        Map.entry("gujarati", "હેલો વર્લ્ડ"),
	        Map.entry("hindi", "हैलो वर्ल्ड"),
	        Map.entry("kannada", "ಹೆಲೋ ವರ್ಲ್ಡ್"),
	        Map.entry("kashmiri", "ہیلو ورلڈ"),
	        Map.entry("maithili", "हैलो वर्ल्ड"),
	        Map.entry("malayalam", "ഹലോ വേൾഡ്"),
	        Map.entry("manipuri", "ꯍꯦꯂꯣ ꯋꯔꯜꯗ"),
	        Map.entry("marathi", "हेलो वर्ल्ड"),
	        Map.entry("nepali", "हेलो वर्ल्ड"),
	        Map.entry("oriya", "ହେଲୋ ୱର୍ଲ୍ଡ"),
	        Map.entry("panjabi", "ਹੈਲੋ ਵਰਲਡ"),
	        Map.entry("sanskrit", "हेलो वर्ल्ड"),
	        Map.entry("santali", "ᱦᱮᱞᱚ ᱣᱟᱲᱞᱰ"),
	        Map.entry("sindhi", "هيلو ورلڊ"),
	        Map.entry("tamil", "ஹெலோ வேர்ல்டு"),
	        Map.entry("telugu", "హలో వరల్డ్"),
	        Map.entry("urdu", "ہیلو ورلڈ"),
	        Map.entry("english", "Hello World")
	    );

	public String getTranslation(String language) 
	{
        return Optional.ofNullable(language)
            .map(String::trim)
            .map(String::toLowerCase)
            .flatMap(lang -> Optional.ofNullable(TRANSLATIONS.get(lang)))
            .orElse("Unknown");
    }
	
	public void selectTTsLanguage(String value)
	{
		SelectDropDownByVisibleText(TTSLanguageSelect, value);
	}
	    
	public boolean validateTTSOutput(String expectedText, String languageName) throws Exception 
	{
	    File wavFile = new File("output.wav");

	    // Step 1: Extract audio
	    WebElement audioElement = driver.findElement(Audio);
	    String src = audioElement.getAttribute("src");
	    if (src == null || !src.startsWith("data:audio")) {
	        logger.log(Status.WARNING, "No base64 audio found.");
	        return false;
	    }

	    byte[] wavBytes = Base64.getDecoder().decode(src.split(",")[1]);
	    FileUtils.writeByteArrayToFile(wavFile, wavBytes);
	    System.out.println("WAV file saved at: " + wavFile.getAbsolutePath());

	    // Step 2: Call Python script with language
	    String scriptPath = Paths.get(System.getProperty("user.dir"), "src", "test", "python", "transcribe.py").toString();
	    ProcessBuilder pb = new ProcessBuilder("python", scriptPath, wavFile.getAbsolutePath(), languageName);
	    pb.redirectErrorStream(true);
	    Process process = pb.start();

	    StringBuilder output = new StringBuilder();
	    try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
	        String line;
	        while ((line = reader.readLine()) != null) {
	            System.out.println("PYTHON >>> " + line);
	            output.append(line).append("\n");
	        }
	    }

	    int exitCode = process.waitFor();
	    if (exitCode != 0) {
	        logger.log(Status.FAIL, "Python script failed with exit code " + exitCode);
	        return false;
	    }

	    // Step 3: Extract result
	    String detectedLang = null, transcription = null, transliterated = null;
	    for (String line : output.toString().split("\n")) {
	        if (line.startsWith("LANGUAGE:")) detectedLang = line.replace("LANGUAGE:", "").trim();
	        if (line.startsWith("TRANSCRIPTION:")) transcription = line.replace("TRANSCRIPTION:", "").trim();
	        if (line.startsWith("TRANSLITERATED:")) transliterated = line.replace("TRANSLITERATED:", "").trim();
	    }

	    logger.log(Status.INFO, "Detected Language  : " + detectedLang);
	    logger.log(Status.INFO, "Expected           : " + expectedText);
	    logger.log(Status.INFO, "ASR Output (raw)   : " + transcription);
	    logger.log(Status.INFO, "ASR Output (native): " + transliterated);

	    return transliterated != null && transliterated.equalsIgnoreCase(expectedText);
	}
	
	public void InputTextForTTS(String value)
	{
		WebElement textarea = driver.findElement(Response);
	    ((JavascriptExecutor) driver).executeScript("arguments[0].value = '';", textarea);
	    textarea.sendKeys(Keys.CONTROL + "a");
	    textarea.sendKeys(Keys.DELETE);
	    textarea.sendKeys(value);
	}
	
	public void clickOnTextSubmitBtn()
	{
		driver.findElement(TextSubmitBtn).click();
	}

	public String getInputTextForLanguage(String language)
	{
	    if (language == null || language.trim().isEmpty()) return "";

	    Map<String, String> textMap = Map.ofEntries(
	        Map.entry("assamese", "আপোনাৰ কেনে?"),
	        Map.entry("bangla", "তুমি কেমন আছো?"),
	        Map.entry("boro", "नोंगनाय गोजाय आफाय?"),
	        Map.entry("dogri", "तुसी केहे हाल ऐ?"),
	        Map.entry("goan-konkani", "तुम कशे आसा?"),
	        Map.entry("gujarati", "કેમ છો?"),
	        Map.entry("hindi", "कैसे हो?"),
	        Map.entry("kannada", "ನೀವು ಹೇಗಿದ್ದೀರಾ?"),
	        Map.entry("kashmiri", "تُہہ ڈپَت چُھ؟"),
	        Map.entry("maithili", "अहाँ कतय छी?"),
	        Map.entry("malayalam", "നിങ്ങൾ എങ്ങനെയുണ്ട്?"),
	        Map.entry("manipuri", "ꯁꯤꯟꯇꯤ ꯑꯃꯗꯨ?"),
	        Map.entry("marathi", "कसे आहात?"),
	        Map.entry("nepali", "तिमीलाई कस्तो छ?"),
	        Map.entry("oriya", "ତୁମେ କେମିତି ଅଛ?"),
	        Map.entry("panjabi", "ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ?"),
	        Map.entry("sanskrit", "कथम् अस्ति भवान्?"),
	        Map.entry("santali", "आदि सेर भेड?"),
	        Map.entry("sindhi", "توهان ڪيئن آهيو؟"),
	        Map.entry("tamil", "நீங்கள் எப்படி இருக்கிறீர்கள்?"),
	        Map.entry("telugu", "మీరు ఎలా ఉన్నారు?"),
	        Map.entry("urdu", "آپ کیسے ہیں؟"),
	        Map.entry("english", "How are you?")
	    );

	    return textMap.getOrDefault(language.trim().toLowerCase(), "");
	}

	public String waitUntilElementVisibleOrTTSFail()
	{
	    By targetElement = WordCountTxt;
	    By shadowHostSelector = By.cssSelector("nextjs-portal");
	    By errorHeadingSelector = By.cssSelector("h1#nextjs__container_errors_label");
	    By closeButtonSelector = By.cssSelector("button[data-nextjs-errors-dialog-left-right-close-button='true']");

	    try {
	        return new WebDriverWait(driver, Duration.ofSeconds(10)).until(d -> {
	            try {
	                List<WebElement> successElements = d.findElements(targetElement);
	                if (!successElements.isEmpty() && successElements.get(0).isDisplayed()) {
	                    return "SUCCESS";
	                }

	                WebElement shadowHost = d.findElement(shadowHostSelector);
	                SearchContext shadowRoot = shadowHost.getShadowRoot();

	                List<WebElement> errorHeadings = shadowRoot.findElements(errorHeadingSelector);
	                if (!errorHeadings.isEmpty() && errorHeadings.get(0).isDisplayed()) {
	                    WebElement closeButton = shadowRoot.findElement(closeButtonSelector);
	                    if (closeButton.isDisplayed()) {
	                        closeButton.click();
	                        Thread.sleep(1000);
	                    }
	                    return "FAILED";
	                }

	            } 
	            catch (NoSuchElementException | StaleElementReferenceException e) 
	            {
	                // Retry silently
	            } 
	            catch (InterruptedException e) 
	            {
	                Thread.currentThread().interrupt();
	            } 
	            catch (Exception e) 
	            {
	                System.out.println("Unexpected error: " + e.getClass().getSimpleName() + " - " + e.getMessage());
	            }

	            return null;
	        });
	    } 
	    catch (TimeoutException e) 
	    {
	        return "TIMEOUT";
	    }
	}

	WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
	
	public void selectLangComboFromDropdown(String combo) 
	{
		WebElement dropdown = wait.until(ExpectedConditions.visibilityOfElementLocated(TranslationSelect));
        Select select = new Select(dropdown);
        select.selectByVisibleText(combo);
	}

	public void InputTranslationText(String value)
	{
		WebElement inputBox = wait.until(ExpectedConditions.visibilityOfElementLocated(TranslationInputBox));
	    ((JavascriptExecutor) driver).executeScript("arguments[0].value = '';", inputBox);
	    inputBox.sendKeys(Keys.CONTROL + "a");
	    inputBox.sendKeys(Keys.DELETE);
        inputBox.sendKeys(value);
	}

	public void clickOnTranslateBtn() 
	{
		 WebElement translateBtn = wait.until(ExpectedConditions.elementToBeClickable(TranslateBtn));
         translateBtn.click();
	}

	public String getTranslatedOutput(String combo) 
	{
		WebElement outputBox = wait.until(ExpectedConditions.visibilityOfElementLocated(TranslationOutputBox));
        wait.until(driver -> !outputBox.getAttribute("value").trim().isEmpty());
        
        String output = outputBox.getAttribute("value").trim();
        System.out.println("Output: " + output);
        logger.log(Status.INFO, "Output for " + combo + ": " + output);
        
        return output;
	}
	
	public List<String> getAllLanguageDropdownOptions() {
	    WebElement dropdown = wait.until(ExpectedConditions.visibilityOfElementLocated(TranslationSelect));
	    Select select = new Select(dropdown);
	    List<WebElement> allOptions = select.getOptions();
	    return allOptions.stream().map(WebElement::getText).map(String::trim).collect(Collectors.toList());
	}
	
	public void clickOnPipelineBtn()
	{
		driver.findElement(PipelineBtn).click();
	}
	
	public void waitUntilPipelineHeaderVisible()
	{
		waitUntillElementVisible(PipelineHeader);
	}
	
	public Select selectSourceLang()
	{
		WebElement sourceSelectEl = wait.until(ExpectedConditions.presenceOfElementLocated(PipelineSource));
        Select sourceSel = new Select(sourceSelectEl);
        
        return sourceSel;
	}
	
	public Select selectTargetLang()
	{
		WebElement targetSelectEl = wait.until(ExpectedConditions.presenceOfElementLocated(PipelineTarget));
        Select targetSel = new Select(targetSelectEl);
        
        return targetSel;
	}
	
	public void selectSourceLanguages(String value)
	{
		SelectDropDownByVisibleText(PipelineSource, value);
	}
	
	public void selectTargetLanguages(String value)
	{
		SelectDropDownByVisibleText(PipelineTarget, value);
	}
	
	public void uploadAudioFile(String filePath) throws Exception	
	{		
		WebElement fileInput = driver.findElement(By.xpath("//input[@type='file']"));
	    fileInput.sendKeys(filePath);
	}
	
	public boolean isSourceTextVisible()
	{
		return driver.findElement(PipelineSourceTextarea).isDisplayed();
	}
	
	public boolean isTargetTextVisible()
	{
		return driver.findElement(PipelineTargetTextarea).isDisplayed();
	}
	
	public String waitUntilElementVisibleOrS2SFail() {
	    By targetElement = WordCountTxt;
	    By shadowHostSelector = By.cssSelector("nextjs-portal");
	    By errorHeadingSelector = By.cssSelector("h1#nextjs__container_errors_label");
	    By closeButtonSelector = By.cssSelector("button[data-nextjs-errors-dialog-left-right-close-button='true']");

	    try {
	        return new WebDriverWait(driver, Duration.ofSeconds(15)).until(d -> {
	            try {
	                // ✅ Check if success element appears
	                List<WebElement> successElements = d.findElements(targetElement);
	                if (!successElements.isEmpty() && successElements.get(0).isDisplayed()) {
	                    return "SUCCESS";
	                }

	                // ✅ Look into shadow host for error dialog
	                WebElement shadowHost = d.findElement(shadowHostSelector);
	                SearchContext shadowRoot = shadowHost.getShadowRoot();

	                List<WebElement> errorHeadings = shadowRoot.findElements(errorHeadingSelector);
	                if (!errorHeadings.isEmpty() && errorHeadings.get(0).isDisplayed()) {
	                    // ✅ Try closing the error dialog (supports nested shadow DOMs)
	                    WebElement closeButton = findElementInShadowDom(shadowRoot, closeButtonSelector, 5);
	                    if (closeButton != null && closeButton.isDisplayed()) {
	                        closeButton.click();
	                        new WebDriverWait(driver, Duration.ofSeconds(2))
	                                .until(ExpectedConditions.invisibilityOf(closeButton));
	                    }
	                    return "FAILED";
	                }

	            } catch (NoSuchElementException | StaleElementReferenceException e) {
	                return null; // keep retrying
	            } catch (Exception e) {
	                System.out.println("Unexpected error: " + e.getClass().getSimpleName() + " - " + e.getMessage());
	            }

	            return null; // keep waiting
	        });
	    } catch (TimeoutException e) {
	        return "TIMEOUT";
	    }
	}

	/**
	 * Recursively searches inside nested shadow DOMs for an element.
	 *
	 * @param context   the starting shadow root or driver
	 * @param selector  the element locator to find
	 * @param maxDepth  how deep to search (safety cap to avoid infinite recursion)
	 * @return the WebElement if found, else null
	 */
	private WebElement findElementInShadowDom(SearchContext context, By selector, int maxDepth) {
	    if (maxDepth <= 0) return null;

	    try {
	        // First, check in current shadow root
	        List<WebElement> elements = context.findElements(selector);
	        if (!elements.isEmpty()) {
	            return elements.get(0);
	        }

	        // Explore child elements for deeper shadow roots
	        List<WebElement> allElements = context.findElements(By.cssSelector("*"));
	        for (WebElement el : allElements) {
	            try {
	                SearchContext innerShadow = el.getShadowRoot();
	                WebElement found = findElementInShadowDom(innerShadow, selector, maxDepth - 1);
	                if (found != null) return found;
	            } catch (UnsupportedOperationException ignored) {
	                // not a shadow host → ignore
	            } catch (Exception innerEx) {
	                System.out.println("Nested shadow lookup failed: " + innerEx.getMessage());
	            }
	        }
	    } catch (Exception ignored) {
	    }

	    return null;
	}
}
