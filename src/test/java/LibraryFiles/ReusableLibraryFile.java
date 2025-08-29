package LibraryFiles;

import java.awt.Toolkit;
import java.awt.datatransfer.Clipboard;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URI;
import java.net.URL;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.Duration;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.HashMap;
import java.util.Properties;
import java.awt.datatransfer.StringSelection;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;

import org.openqa.selenium.By;
import org.openqa.selenium.Dimension;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.remote.RemoteWebDriver;
import org.openqa.selenium.remote.SessionId;
import org.apache.commons.configuration2.PropertiesConfiguration;
import org.apache.commons.configuration2.builder.FileBasedConfigurationBuilder;
import org.apache.commons.configuration2.builder.fluent.Configurations;
import org.apache.commons.configuration2.ex.ConfigurationException;

import org.apache.commons.io.FileUtils;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.DataFormatter;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.xssf.usermodel.XSSFRow;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.ss.usermodel.Workbook;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.Keys;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;
import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.interactions.PointerInput;
import org.openqa.selenium.interactions.Sequence;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.ITestResult;

import com.aventstack.extentreports.ExtentReports;
import com.aventstack.extentreports.ExtentTest;
import com.aventstack.extentreports.Status;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;

public class ReusableLibraryFile {

	// Global variables goes here
	public static WebDriver driver;

	Path path = Paths.get(System.getProperty("user.dir"), "GlobalSettings.properties");
	String PropertiesFilePath = path.toString();

	public static ExtentTest logger;
	public static ExtentReports extent;
	public static String browser;

	public static AndroidDriver adriver;

	public void OpenBrowserInstance() throws Exception {
		System.out.println("Setting up driver by initializing browser instance");
		String WSpath = System.getProperty("user.dir");
		String downloadFilepath = Paths.get(WSpath, "TestDownloads").toString();
		browser = GetPropertyFileValue("Browser");

		try {
			String normalizedDownloadDir = Paths.get(downloadFilepath).toAbsolutePath().toString();

			if (browser.equalsIgnoreCase("Chrome")) {
				System.out.println("Opening Google Chrome Browser Instance");
				WebDriverManager.chromedriver().setup();

				HashMap<String, Object> prefs = new HashMap<>();
				prefs.put("profile.default_content_settings.popups", 0);
				prefs.put("download.default_directory", normalizedDownloadDir);

				String WAVFilepath = Paths.get(WSpath, "TestData", "Recording.wav").toString();
				ChromeOptions options = new ChromeOptions();
				options.setExperimentalOption("prefs", prefs);
				options.setAcceptInsecureCerts(true);
				options.addArguments("--remote-allow-origins=*", "--incognito", "--allow-file-access-from-files",
						"--allow-insecure-localhost", "--ignore-certificate-errors", "--disable-features=HttpsOnlyMode",
						"--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream",
						"--disable-notifications", "--use-file-for-fake-audio-capture=" + WAVFilepath);

				driver = new ChromeDriver(options);
			} else if (browser.equalsIgnoreCase("Firefox")) {
				System.out.println("Opening Mozilla Firefox Browser Instance");
				WebDriverManager.firefoxdriver().setup();

				FirefoxOptions options = new FirefoxOptions();

				// download prefs
				options.addPreference("browser.download.dir", normalizedDownloadDir);
				options.addPreference("browser.download.folderList", 2);
				options.addPreference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream");
				options.addPreference("pdfjs.disabled", true);
				options.setAcceptInsecureCerts(true);

				// media + incognito
				options.addArguments("-private");
				options.addArguments("--use-fake-device-for-media-stream");
				options.addArguments("--use-fake-ui-for-media-stream");
				String WAVFilepath = Paths.get(WSpath, "TestData", "Recording.wav").toString();
				options.addArguments("--use-file-for-fake-audio-capture=" + WAVFilepath);

				driver = new FirefoxDriver(options);
			} else if (browser.equalsIgnoreCase("Edge")) {
				System.out.println("Opening Microsoft Edge Browser Instance");
				WebDriverManager.edgedriver().setup();

				HashMap<String, Object> prefs = new HashMap<>();
				prefs.put("profile.default_content_settings.popups", 0);
				prefs.put("download.default_directory", normalizedDownloadDir);

				EdgeOptions options = new EdgeOptions();
				options.setExperimentalOption("prefs", prefs);
				options.setAcceptInsecureCerts(true);

				String WAVFilepath = Paths.get(WSpath, "TestData", "Recording.wav").toString();
				options.addArguments("--remote-allow-origins=*");
				options.addArguments("inprivate");
				options.addArguments("--allow-file-access-from-files");
				options.addArguments("--use-fake-device-for-media-stream");
				options.addArguments("--use-fake-ui-for-media-stream");
				options.addArguments("--disable-notifications");
				options.addArguments("--ignore-certificate-errors");
				options.addArguments("--allow-insecure-localhost");
				options.addArguments("--use-file-for-fake-audio-capture=" + WAVFilepath);

				driver = new EdgeDriver(options);
			} else {
				throw new IllegalArgumentException("Unsupported browser: " + browser);
			}

		} catch (Exception e) {
			System.err.println("Driver initialization failed: " + e.getMessage());
			e.printStackTrace();
		}

		driver.manage().window().maximize();
		driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(40));
		driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(25));

	}

	public String GetPropertyFileValue(String Key) throws IOException {
		Properties obj = new Properties();
		FileInputStream objfile = new FileInputStream(PropertiesFilePath);
		obj.load(objfile);
		String value = obj.getProperty(Key);
		return value;
	}

	public String GetPropertyFileValue(String dataFilePath, String Key) throws IOException {
		Properties obj = new Properties();
		FileInputStream objfile = new FileInputStream(dataFilePath);
		obj.load(objfile);
		String value = obj.getProperty(Key);
		return value;
	}

	public void LaunchMobApplication() throws Exception {
		System.out.println("Setting up driver by initializing app instance");
		String WSpath = System.getProperty("user.dir");
		String appPath = Paths.get(WSpath, "").toString();

		DesiredCapabilities capabilities = new DesiredCapabilities();

		capabilities.setCapability("appium:deviceName", GetPropertyFileValue("DeviceName"));
		capabilities.setCapability("appium:udid", GetPropertyFileValue("DeviceUDID"));
		capabilities.setCapability("appium:platformName", "Android");
		capabilities.setCapability("appium:automationName", "UiAutomator2");
		capabilities.setCapability("appium:app", appPath);
		capabilities.setCapability("appium:platformVersion", GetPropertyFileValue("AndroidVersion"));
		capabilities.setCapability("appium:appPackage", "org.nest.IdenTTApp");
		capabilities.setCapability("appium:appActivity", "org.nest.IdenTTApp.ui.activities.main.MainActivity");
		capabilities.setCapability("appium:newCommandTimeout", 300);
		capabilities.setCapability("appium:adbExecTimeout", 50000); // This increases timeout for ADB commands
		capabilities.setCapability("appium:noReset", false);
		capabilities.setCapability("appium:adb_shell", true); // Enable adb_shell

		URL url = URI.create("http://127.0.0.1:4723/").toURL();

		adriver = new AndroidDriver(url, capabilities);

		Thread.sleep(2000);
		System.out.println("Application Started\n\n");
		Thread.sleep(5000);

	}

	public void quitActiveDrivers() {
		// Quit AndroidDriver if initialized and session still alive
		try {
			if (adriver != null && adriver.getSessionId() != null) {
				System.out.println("Ending Appium session: " + adriver.getSessionId());
				adriver.quit();
				System.out.println("Appium session quit successfully.");
			}
		} catch (Exception e) {
			System.err.println("Error quitting AndroidDriver: " + e.getMessage());
		} finally {
			adriver = null;
		}

		// Quit WebDriver if initialized and session still alive
		try {
			if (driver != null) {
				SessionId webSession = null;
				if (driver instanceof RemoteWebDriver) {
					webSession = ((RemoteWebDriver) driver).getSessionId();
				}
				if (webSession != null) {
					System.out.println("Ending Selenium session: " + webSession);
					driver.quit();
					System.out.println("Selenium session quit successfully.");
				}
			}
		} catch (Exception e) {
			System.err.println("Error quitting WebDriver: " + e.getMessage());
		} finally {
			driver = null;
		}
	}

	public void LaunchWebApplication(String username, String password) throws Exception {
		By ContinueToSiteBtn = By.xpath("//button[contains(text(), 'Continue to site')]");
		By LoggedInHeader = By.xpath("//h2[contains(text(), 'Login into Dhruva')]");

		String baseUrl = GetPropertyFileValue("BaseUrl");
		driver.get(baseUrl);

		waitUntillElementVisible(ContinueToSiteBtn);
		Thread.sleep(1000);
		driver.findElement(ContinueToSiteBtn).click();

		waitUntillElementVisible(LoggedInHeader);
		Thread.sleep(1000);
	}

	public void LoginToApplication() throws Exception {
		By UserName = By.xpath("//input[@placeholder='Username']");
		By Password = By.xpath("//input[@placeholder='Password']");
		By LoginBtn = By.xpath("//button[contains(text(), 'LOGIN')]");
		By LoginHeader = By.xpath("//h2[contains(text(), 'Login into Dhruva')]");
		By LoggedInHeader = By.xpath("//p[contains(text(), 'Services')]");

		waitUntillElementVisible(LoginHeader);
		Thread.sleep(1000);

		System.out.println("Landed on Dhruva Portal Login Page\n");
		logger.log(Status.INFO, "Landed on Dhruva Portal Login Page");

		System.out.println("Entering Username in the Username field\n");
		logger.log(Status.INFO, "Entering Username in the Username field");
		driver.findElement(UserName).sendKeys(GetPropertyFileValue("Username"));

		System.out.println("Entering Password in the Password field\n");
		logger.log(Status.INFO, "Entering Password in the Password field");
		driver.findElement(Password).sendKeys(GetPropertyFileValue("Password"));

		System.out.println("Clicking on the Log In Button to proceed to OTP Page\n");
		logger.log(Status.INFO, "Clicking on the Log In Button to proceed to OTP Page");
		driver.findElement(LoginBtn).click();

		waitUntillElementVisible(LoggedInHeader);
		Thread.sleep(2000);
	}

	public void ClickOnControl(By Element) {
		WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
		wait.until(ExpectedConditions.visibilityOfElementLocated(Element));
		driver.findElement(Element).click();
	}

	public void SendValueToInputControl(By Element, String value) throws InterruptedException {
		WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
		wait.until(ExpectedConditions.visibilityOfElementLocated(Element));
		WebElement control = driver.findElement(Element);
		control.clear();
		Thread.sleep(1000);
		control.sendKeys(value);
		Thread.sleep(1000);
	}

	public void waitUntillElementVisible(By element) {
		WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(100));
		wait.until(ExpectedConditions.visibilityOfElementLocated(element));
	}

	public void waitUntilMobElementVisible(By element) {
		WebDriverWait wait = new WebDriverWait(adriver, Duration.ofSeconds(100));
		wait.until(ExpectedConditions.visibilityOfElementLocated(element));
	}

	public void waitUntillElementClickable(By element) {
		WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(100));
		wait.until(ExpectedConditions.elementToBeClickable(element));
	}

	public boolean IsElementClickable(By Element) throws InterruptedException {

		WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
		wait.until(ExpectedConditions.elementToBeClickable(Element));
		WebElement control = driver.findElement(Element);
		return control.isEnabled();
	}

	public boolean IsMobElementClickable(By Element) throws InterruptedException {

		WebDriverWait wait = new WebDriverWait(adriver, Duration.ofSeconds(10));
		wait.until(ExpectedConditions.elementToBeClickable(Element));
		WebElement control = adriver.findElement(Element);
		return control.isEnabled();
	}

	public boolean IsElementVisible(By Element) throws InterruptedException {
		WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
		wait.until(ExpectedConditions.visibilityOfElementLocated(Element));
		WebElement control = driver.findElement(Element);
		return control.isDisplayed();
	}

	public boolean IsElementPresent(By Elements) throws InterruptedException {
		Thread.sleep(1000);
		List<WebElement> controls = driver.findElements(Elements);
		if (controls.size() <= 0)
			return false;
		else
			return true;
	}

	public void SelectDropDownByVisibleText(By Element, String visibleText) {
		WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
		wait.until(ExpectedConditions.visibilityOfElementLocated(Element));
		WebElement element = driver.findElement(Element);
		Select select = new Select(element);
		select.selectByVisibleText(visibleText);
	}

	public void TakeScreenShot(ITestResult result) throws Exception {
		// Check if the screenshot has already been captured for this test
		if (result.getAttribute("screenshotCaptured") != null && (boolean) result.getAttribute("screenshotCaptured")) {
			return;
		}
		result.setAttribute("screenshotCaptured", true);

		String basePath = System.getProperty("user.dir");

		DateFormat df = new SimpleDateFormat("ddMMyy_HHmmss");
		String timestamp = df.format(new Date());

		String statusFolder = switch (result.getStatus()) {
		case ITestResult.SUCCESS -> "Passed";
		case ITestResult.FAILURE, ITestResult.SKIP -> "Failed_Skipped";
		default -> "Other";
		};

		Path screenshotDir = Paths.get(basePath, "ScreenShots", statusFolder);
		File screenshotFolder = screenshotDir.toFile();
		if (!screenshotFolder.exists()) {
			screenshotFolder.mkdirs(); // Create folder if it doesn't exist
		}

		String screenshotFileName = "SnapAt_" + timestamp + ".jpeg";
		File destFile = new File(screenshotFolder, screenshotFileName);

		File srcFile = null;

		try {
			if (driver != null && driver instanceof TakesScreenshot) {
				srcFile = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
			} else if (adriver != null && adriver instanceof TakesScreenshot) {
				srcFile = ((TakesScreenshot) adriver).getScreenshotAs(OutputType.FILE);
			} else {
				System.err.println("Both driver and adriver are null or not screenshot-capable.");
				return;
			}
		} catch (Exception e) {
			System.err.println("Error while taking screenshot: " + e.getMessage());
			return;
		}

		FileUtils.copyFile(srcFile, destFile);

		String relativePath = Paths.get("ScreenShots", statusFolder, screenshotFileName).toString();

		switch (result.getStatus()) {
		case ITestResult.SUCCESS:
			logger.log(Status.PASS,
					"Test passed. Screenshot captured: " + logger.addScreenCaptureFromPath(relativePath));
			break;
		case ITestResult.FAILURE:
			logger.log(Status.FAIL,
					"Test failed. Screenshot captured: " + logger.addScreenCaptureFromPath(relativePath));
			break;
		case ITestResult.SKIP:
			logger.log(Status.SKIP,
					"Test skipped. Screenshot captured: " + logger.addScreenCaptureFromPath(relativePath));
			break;
		}
	}

	public String getText(By Element) {
		WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
		wait.until(ExpectedConditions.visibilityOfElementLocated(Element));
		return driver.findElement(Element).getText().trim();
	}

	public void ScrollDownToGivenPixels(int num) throws Exception {
		JavascriptExecutor js = (JavascriptExecutor) driver;
		js.executeScript("window.scrollBy(0," + num + ")");
		Thread.sleep(2000);
	}

	public void ScrollUpToGivenPixels(int num) throws Exception {
		JavascriptExecutor js = (JavascriptExecutor) driver;
		js.executeScript("window.scrollBy(0,-" + num + ")");
		Thread.sleep(2000);
	}

	public String[] readExcelData(String filePath, String sheet) throws IOException {
		String strValue = "";
		int index = 0;
		FileInputStream fis = new FileInputStream(filePath);
		Workbook fileName = new XSSFWorkbook(fis);
		Sheet sheetName = fileName.getSheet(sheet);
		int rowSize = sheetName.getLastRowNum() + 1;
		String Values[] = new String[rowSize];
		for (int rowNum = 0; rowNum < rowSize; rowNum++) {
			Row row = sheetName.getRow(rowNum);
			for (int colNum = 0; colNum < row.getLastCellNum(); colNum++) {
				Cell cell = row.getCell(colNum);
				DataFormatter dataFormatter = new DataFormatter();
				strValue = dataFormatter.formatCellValue(cell);
				Values[index] = strValue;
				index++;
			}
		}

		fileName.close();

		return Values;
	}

	public int[] readNumericExcelData(String filePath, String sheet) throws IOException {
		int NumValue = 0;
		int index = 0;
		FileInputStream fis = new FileInputStream(filePath);
		Workbook fileName = new XSSFWorkbook(fis);
		Sheet sheetName = fileName.getSheet(sheet);
		int rowSize = sheetName.getLastRowNum() + 1;
		int Values[] = new int[rowSize];
		for (int rowNum = 0; rowNum < rowSize; rowNum++) {
			Row row = sheetName.getRow(rowNum);
			for (int colNum = 0; colNum < row.getLastCellNum(); colNum++) {
				Cell cell = row.getCell(colNum);

				NumValue = (int) cell.getNumericCellValue();
				Values[index] = NumValue;
				index++;
			}
		}

		fileName.close();

		return Values;
	}

	public void writeExcelData(String filePath, String value) throws IOException {

		File file = new File(filePath);

		// Check if the file exists
		if (!file.exists()) {
			throw new FileNotFoundException("The specified file does not exist: " + filePath);
		}

		try (FileInputStream fis = new FileInputStream(file); XSSFWorkbook workbook = new XSSFWorkbook(fis)) {

			XSSFSheet sheet = workbook.getSheetAt(0);
			int rowSize = sheet.getLastRowNum();

			// Find the next empty row (after the last existing row)
			int nextRow = rowSize + 1;

			// Create a new row for the next entry
			XSSFRow row = sheet.createRow(nextRow);

			// Create a cell in the new row and set its value
			row.createCell(0).setCellValue(value);
			System.out.println("Writing value: " + value + " to row: " + nextRow);

			// Write to the file
			try (FileOutputStream fos = new FileOutputStream(file)) {
				workbook.write(fos);
				System.out.println("Data written successfully.");
			}
		}
	}

	// Row count in a sheet
	public int getRowCount(String excelPath, String sheetName) throws IOException {
		File file = new File(excelPath);
		FileInputStream fis = new FileInputStream(file);
		XSSFWorkbook workbook = new XSSFWorkbook(fis);
		int index = workbook.getSheetIndex(sheetName);
		XSSFSheet sheet = workbook.getSheetAt(index);
		int numberOfRows = sheet.getLastRowNum() + 1;
		workbook.close();
		return numberOfRows;
	}

	public static int countFilesInGivenDirectory(File directory) {
		int count = 0;
		for (File file : directory.listFiles()) {
			if (file.isFile()) {
				count++;
			}
		}
		return count;
	}

	public void CopyPasteGivenStringToElement(By element, String value) {
		Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
		StringSelection str = new StringSelection(value);
		clipboard.setContents(str, null);
		WebElement inputBox = driver.findElement(element);
		inputBox.clear();
		inputBox.sendKeys(Keys.CONTROL, "V");
	}

	public void UpdateKeyValueInGlobalPropertyFile(String key, String value) throws ConfigurationException {

		File configFile = new File(PropertiesFilePath);

		Configurations configs = new Configurations();
		PropertiesConfiguration config = configs.properties(configFile);

		config.setProperty(key, value);

		FileBasedConfigurationBuilder<PropertiesConfiguration> builder = new FileBasedConfigurationBuilder<PropertiesConfiguration>(
				PropertiesConfiguration.class)
				.configure(new org.apache.commons.configuration2.builder.fluent.Parameters().fileBased()
						.setFile(configFile));
		builder.save();
	}

	public static int countFilesInCurrentDirectory(File directory) {
		int count = 0;
		for (File file : directory.listFiles()) {
			if (file.isFile()) {
				count++;
			}
		}
		return count;
	}

	public String getPastDateInformat(int num, String format) {
		SimpleDateFormat dateFormat = new SimpleDateFormat(format);
		Calendar cal = Calendar.getInstance();
		cal.add(Calendar.DATE, -num);
		return dateFormat.format(cal.getTime());
	}

	public String getDateInformat(int num, String format) {
		SimpleDateFormat dateFormat = new SimpleDateFormat(format);
		Calendar cal = Calendar.getInstance();
		cal.add(Calendar.DATE, num);
		return dateFormat.format(cal.getTime());
	}

	public String getDateBeforeGivenDate(String strDate, String format) throws Exception {
		SimpleDateFormat sdf = new SimpleDateFormat(format);
		Date date = sdf.parse(strDate);
		Calendar calendar = Calendar.getInstance();
		calendar.setTime(date);
		calendar.add(Calendar.DATE, -1);
		Date yesterday = calendar.getTime();
		return sdf.format(yesterday);
	}

	public static void updatePropertyFile(String filePath, String key, String newValue) throws IOException {
		Path path = Path.of(filePath);
		List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
		String prefix = key + "=";
		boolean found = false;

		for (int i = 0; i < lines.size(); i++) {
			String line = lines.get(i);
			// skip comments and blank lines
			if (line.trim().startsWith("#") || line.trim().isEmpty()) {
				continue;
			}
			// if this line sets our key, replace it
			if (line.startsWith(prefix)) {
				lines.set(i, prefix + newValue);
				found = true;
				break;
			}
		}

		// if the key wasn't already in the file, append it at the end:
		if (!found) {
			lines.add("");
			lines.add(prefix + newValue);
		}

		// write back all lines, preserving original newline structure
		Files.write(path, lines, StandardCharsets.UTF_8, StandardOpenOption.TRUNCATE_EXISTING);
	}

	public void ScrollToGivenElement(WebElement Element) throws Exception {
		JavascriptExecutor js = (JavascriptExecutor) driver;
		js.executeScript("arguments[0].scrollIntoView();", Element);
		Thread.sleep(2000);
	}

	public void ScrollDownToBottomOfWebpage() {
		JavascriptExecutor js = (JavascriptExecutor) driver;

		js.executeScript("window.scrollTo(0, document.body.scrollHeight);");

		new WebDriverWait(driver, Duration.ofSeconds(5)).until(webDriver -> {
			Number scrollY = (Number) js.executeScript("return window.scrollY + window.innerHeight;");
			Number pageHeight = (Number) js.executeScript("return document.body.scrollHeight;");
			return scrollY.longValue() >= pageHeight.longValue() - 2;
		});
	}

	public void ScrollUpToTopOfWebpage() {
		JavascriptExecutor js = (JavascriptExecutor) driver;

		js.executeScript("window.scrollTo(0, 0);");

		new WebDriverWait(driver, Duration.ofSeconds(5)).until(webDriver -> {
			Number offset = (Number) js.executeScript("return window.pageYOffset;");
			return offset.longValue() == 0L;
		});
	}

	public String SetGivenDate(String strDate, String format) throws Exception {
		SimpleDateFormat sdf = new SimpleDateFormat(format);
		Date date = sdf.parse(strDate);
		Calendar calendar = Calendar.getInstance();
		calendar.setTime(date);
		Date today = calendar.getTime();
		return sdf.format(today);
	}

	public void ScrollRightToGivenPixels(int num) throws Exception {
		WebElement element = driver
				.findElement(By.xpath("//div[@id='previousPackage_popup']//div[@class='modal-content']/div[2]"));
		JavascriptExecutor js = (JavascriptExecutor) driver;
		js.executeScript("arguments[0].scrollBy(" + num + ",0)", element);
		Thread.sleep(2000);

	}

	public void scrollUntilElementVisible(By targetLocator, double maxLimit, boolean scrollDown) throws Exception {
		Dimension size = adriver.manage().window().getSize();
		int startX = size.width / 2;
		int startY = (int) (size.height * (scrollDown ? maxLimit : 0.2));
		int endY = (int) (size.height * (scrollDown ? 0.2 : maxLimit));

		PointerInput finger = new PointerInput(PointerInput.Kind.TOUCH, "finger1");
		Sequence swipe = new Sequence(finger, 1)
				.addAction(
						finger.createPointerMove(Duration.ofMillis(0), PointerInput.Origin.viewport(), startX, startY))
				.addAction(finger.createPointerDown(PointerInput.MouseButton.LEFT.asArg()))
				.addAction(
						finger.createPointerMove(Duration.ofMillis(300), PointerInput.Origin.viewport(), startX, endY))
				.addAction(finger.createPointerUp(PointerInput.MouseButton.LEFT.asArg()));

		int attempts = 0;
		while (adriver.findElements(targetLocator).isEmpty()) {
			if (++attempts > 10) {
				// optional native fallback once:
				try {
					String uiScroll = "new UiScrollable(new UiSelector().scrollable(true))"
							+ ".scrollIntoView(new UiSelector()." + locatorToUiSelector(targetLocator) + ");";
					adriver.findElement(AppiumBy.androidUIAutomator(uiScroll));
					break;
				} catch (Exception e) {
					throw new NoSuchElementException("Could not find element after " + 10 + " swipes: " + targetLocator,
							e);
				}
			}
			adriver.perform(Collections.singletonList(swipe));
			// tiny pause if needed:
			try {
				Thread.sleep(300);
			} catch (InterruptedException ignored) {
			}
		}
	}

	private String locatorToUiSelector(By by) {
		String s = by.toString();
		if (s.contains("By.id: ")) {
			String id = s.split("By.id: ")[1];
			return "resourceId(\"" + id + "\")";
		} else if (s.contains("By.accessibilityId: ")) {
			String acc = s.split("By.accessibilityId: ")[1];
			return "description(\"" + acc + "\")";
		}
		throw new IllegalArgumentException("Unsupported locator for UiScrollable fallback: " + by);
	}

	public void SwipeDownThroughEntireScreen(int startX, int startY, int endX, int endY) {
		PointerInput finger = new PointerInput(PointerInput.Kind.TOUCH, "finger1");
		Sequence sequence = new Sequence(finger, 1)
				.addAction(
						finger.createPointerMove(Duration.ofMillis(0), PointerInput.Origin.viewport(), startX, startY))
				.addAction(finger.createPointerDown(PointerInput.MouseButton.LEFT.asArg()))
				.addAction(
						finger.createPointerMove(Duration.ofMillis(1000), PointerInput.Origin.viewport(), endX, endY))
				.addAction(finger.createPointerUp(PointerInput.MouseButton.LEFT.asArg()));

		adriver.perform(Arrays.asList(sequence));
	}

	public void SwipeToBottomScreen() {
		Dimension screenSize = adriver.manage().window().getSize();
		int width = screenSize.width;
		int height = screenSize.height;

		int startX = width / 2;
		int startY = (int) (height * 0.8);
		int endY = (int) (height * 0.2);

		PointerInput finger = new PointerInput(PointerInput.Kind.TOUCH, "finger1");
		Sequence swipe = new Sequence(finger, 1);

		swipe.addAction(finger.createPointerMove(Duration.ZERO, PointerInput.Origin.viewport(), startX, startY));
		swipe.addAction(finger.createPointerDown(PointerInput.MouseButton.LEFT.asArg()));
		swipe.addAction(
				finger.createPointerMove(Duration.ofMillis(1000), PointerInput.Origin.viewport(), startX, endY));
		swipe.addAction(finger.createPointerUp(PointerInput.MouseButton.LEFT.asArg()));

		adriver.perform(Arrays.asList(swipe));
	}

}
