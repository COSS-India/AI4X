package Configuration;

import java.util.Date;

public class TestStatistics extends TestListeners {

	public static int passedTestcases;
	public static int failedTestcases;
	public static int skippedTestcases;
	public static int total;
	public static Date startedDatetime;
	public static long startedTime;
	public static long EndTime;
	public static long diffTime;
	public static Date EndDatetime;

	public static void printSuiteStatistics() {
		passedTestcases = PassedTests.size();
		failedTestcases = FailedTests.size();
		skippedTestcases = SkippedTests.size();
		total = passedTestcases + failedTestcases + skippedTestcases;
		System.out.println("");
		System.out.println(" Passed testcases: " + passedTestcases);
		System.out.println(" Failed testcases: " + failedTestcases);
		System.out.println(" Skipped testcases: " + skippedTestcases);
		System.out.println("=======================================");
		System.out.println(" Total testcases: " + total);
		System.out.println("=======================================");

	}
}
