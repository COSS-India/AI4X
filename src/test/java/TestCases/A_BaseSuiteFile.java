package TestCases;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.testng.ITestResult;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.AfterSuite;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.BeforeSuite;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Listeners;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;
import com.aventstack.extentreports.ExtentReports;
import com.aventstack.extentreports.Status;
//import com.aventstack.extentreports.reporter.ExtentHtmlReporter;
import com.aventstack.extentreports.reporter.ExtentSparkReporter;

import Configuration.TestStatistics;
import LibraryFiles.ReusableLibraryFile;

@SuppressWarnings("unused")
@Listeners(Configuration.TestListeners.class)
public class A_BaseSuiteFile extends ReusableLibraryFile {

	public String RefID = "";
	
	// Declare test class objects here//
	DhruvaPortalTests obj_DhruvaPortalTests;
	DhruvaAPITests obj_DhruvaAPITests;

		
	@BeforeSuite(alwaysRun = true)
	public void beforeSuite() {
		System.out.println("========Test Suite Started===========");
	}

	@AfterSuite(alwaysRun = true)
	public void afterSuite() {
		System.out.println("========Test Suite Ends===========");
	}

	@BeforeTest(alwaysRun = true)
	public void beforeTest() throws IOException {
		System.out.println("Configuring extend reports...");
		String baseUrl = GetPropertyFileValue("BaseUrl");
		browser = GetPropertyFileValue("Browser");
		DateFormat df = new SimpleDateFormat("ddMMyy_HHmmss");
		Date dateobj = new Date();
		String subString = df.format(dateobj);
		
		Path path = Paths.get(System.getProperty("user.dir"), "TestReports", "HtmlReport_" + subString + ".html");
		String ExtentFilePath = path.toString();

		ExtentSparkReporter htmlReporter = new ExtentSparkReporter(ExtentFilePath);
		extent = new ExtentReports();
		extent.attachReporter(htmlReporter);
		extent.setSystemInfo("Application Name", "AI4X");
		extent.setSystemInfo("Environment", "Automation Testing");
		extent.setSystemInfo("Automation Tester", "Saikat Aich");
		extent.setSystemInfo("URL", baseUrl);
		extent.setSystemInfo("Browser", browser);
		extent.setSystemInfo("Version", "V1.0");
	}

	@BeforeClass(alwaysRun = true)
	// instantiate object here
	public void beforeClass() {
		System.out.println("Instantiating Test classes....");

		obj_DhruvaPortalTests = new DhruvaPortalTests();
		obj_DhruvaAPITests = new DhruvaAPITests();

	}

	@BeforeMethod(alwaysRun = true)
	public void beforeMethod(Method testMethod) throws Exception {
		logger = extent.createTest(testMethod.getName(), testMethod.getAnnotation(Test.class).description());

		
	}

	@AfterMethod(alwaysRun = true)
	public void afterMethod(ITestResult result) throws Exception {
		System.out.println("\nClosing browser instance....");
		if (result.getStatus() == ITestResult.FAILURE) {
			logger.log(Status.INFO, "Testcase failed is: " + result.getName());
			logger.log(Status.INFO, "failure is: " + result.getThrowable());
		} else if (result.getStatus() == ITestResult.SKIP) {
			logger.log(Status.INFO, "Testcase skipped is: " + result.getName());
		}
		TakeScreenShot(result);
		System.out.println("Closing driver instance");
		System.out.println("\n===================================================================================\n");
		quitActiveDrivers();
		logger.log(Status.INFO, "Closed driver instance(s) for given test");
	}

	@AfterTest(alwaysRun = true)
	public void afterTest() {
		System.out.println("Closing extend report instance");
		TestStatistics.printSuiteStatistics();
		extent.flush();
	}

	/*
	 * Start of TestCases
	 * =================================================================================================================
	 * =================================================================================================================
	 */	

	
	@Test(enabled=true, groups= {"FullSuite", "ASR"}, invocationCount = 1)
	public void TC01_OpenDhruvaPortalAndTestASRForAllLanguages() throws Exception	
	{
		System.out.println("Starting Test method....");

		OpenBrowserInstance();
		String username = GetPropertyFileValue("Username");
		String password = GetPropertyFileValue("Password");
		LaunchWebApplication(username, password);
		
		logger.log(Status.INFO, "Launched application in given browser");
		logger.log(Status.INFO, "Test: TC01_OpenDhruvaPortalAndTestASRForAllLanguages started");
		obj_DhruvaPortalTests.OpenDhruvaPortalAndTestASRForAllLanguages();
	}
	
	@Test(enabled=true, groups= {"FullSuite", "TTS"}, invocationCount = 1)
	public void TC02_OpenDhruvaPortalAndTestTTSForAllLanguages() throws Exception	
	{
		System.out.println("Starting Test method....");

		OpenBrowserInstance();
		String username = GetPropertyFileValue("Username");
		String password = GetPropertyFileValue("Password");
		LaunchWebApplication(username, password);
		
		logger.log(Status.INFO, "Launched application in given browser");
		logger.log(Status.INFO, "Test: TC02_OpenDhruvaPortalAndTestTTSForAllLanguages started");
		obj_DhruvaPortalTests.OpenDhruvaPortalAndTestTTSForAllLanguages();
	}
	
	@Test(enabled=true, groups= {"FullSuite", "Translation"}, invocationCount = 1)
	public void TC03_OpenDhruvaPortalAndTestTranslationForAllLanguages() throws Exception	
	{
		System.out.println("Starting Test method....");

		OpenBrowserInstance();
		String username = GetPropertyFileValue("Username");
		String password = GetPropertyFileValue("Password");
		LaunchWebApplication(username, password);
		
		logger.log(Status.INFO, "Launched application in given browser");
		logger.log(Status.INFO, "Test: TC03_OpenDhruvaPortalAndTestTranslationForAllLanguages started");
		obj_DhruvaPortalTests.OpenDhruvaPortalAndTestTranslationForAllLanguages();
	}
	
	@Test(enabled=true, groups= {"FullSuite", "S2S"}, invocationCount = 1)
	public void TC04_OpenDhruvaPortalAndTestS2SForAllLanguages() throws Exception	
	{
		System.out.println("Starting Test method....");

		OpenBrowserInstance();
		String username = GetPropertyFileValue("Username");
		String password = GetPropertyFileValue("Password");
		LaunchWebApplication(username, password);
		
		logger.log(Status.INFO, "Launched application in given browser");
		logger.log(Status.INFO, "Test: TC04_OpenDhruvaPortalAndTestS2SForAllLanguages started");
		obj_DhruvaPortalTests.OpenDhruvaPortalAndTestS2SForAllLanguages();
	}
	
	@Test(enabled=true, groups= {"FullSuite", "TTS-API"}, invocationCount = 1)
    public void TC05_RunTTSAPIAndCheckResponse() throws Exception
	{
		System.out.println("Starting Test method....");

		logger.log(Status.INFO, "Launched application in given browser");
		logger.log(Status.INFO, "Test: TC05_RunTTSAPIAndCheckResponse started");
		obj_DhruvaAPITests.RunTTSAPIAndCheckResponse();
    }
	
	@Test(enabled=true, groups= {"FullSuite", "Translation-API"}, invocationCount = 1)
    public void TC06_RunTranslationAPIAndCheckResponse() throws Exception
	{
		System.out.println("Starting Test method....");

		logger.log(Status.INFO, "Launched application in given browser");
		logger.log(Status.INFO, "Test: TC06_RunTranslationAPIAndCheckResponse started");
		obj_DhruvaAPITests.RunTranslationAPIAndCheckResponse();
    }
	
	@Test(enabled=true, groups= {"FullSuite", "ASR-API"}, invocationCount = 1)
    public void TC07_RunASRAPIAndCheckResponse() throws Exception
	{
		System.out.println("Starting Test method....");

		logger.log(Status.INFO, "Launched application in given browser");
		logger.log(Status.INFO, "Test: TC07_RunASRAPIAndCheckResponse started");
		obj_DhruvaAPITests.RunASRAPIAndCheckResponse();
    }
	
	@Test(enabled=true, groups= {"FullSuite", "NMT-API"}, invocationCount = 1)
    public void TC08_runTranslationLanguageTestsFromJSON() throws Exception
	{
		System.out.println("Starting Test method....");

		logger.log(Status.INFO, "Launched application in given browser");
		logger.log(Status.INFO, "Test: TC08_runTranslationLanguageTestsFromJSON started");
		obj_DhruvaAPITests.runTranslationLanguageTestsFromJSON();
    }
	
	@Test(enabled=true, groups= {"FullSuite", "TTS-API"}, invocationCount = 1)
    public void TC09_runTTSLanguageTestsFromJSON() throws Exception
	{
		System.out.println("Starting Test method....");

		logger.log(Status.INFO, "Launched application in given browser");
		logger.log(Status.INFO, "Test: TC09_runTTSLanguageTestsFromJSON started");
		obj_DhruvaAPITests.runTTSLanguageTestsFromJSON();
    }
	
	@Test(enabled=true, groups= {"FullSuite", "ASR-API"}, invocationCount = 1)
    public void TC10_runASRLanguageTestsFromJSON() throws Exception
	{
		System.out.println("Starting Test method....");

		logger.log(Status.INFO, "Launched application in given browser");
		logger.log(Status.INFO, "Test: TC10_runASRLanguageTestsFromJSON started");
		obj_DhruvaAPITests.runASRLanguageTestsFromJSON();
    }
}
