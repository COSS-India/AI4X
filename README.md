# AI4X Automation Test Scripts — README

> **Version:** August 2025  
> **Scope:** Automated tests for the **AI4X (Dhruva) Web Portal** and **Inference Model APIs** using **Selenium**, **TestNG**, and **RestAssured**.

---

## Introduction
This README explains how to set up, configure, and run the automated test suites for the AI4X (Dhruva) portal and Inference Model APIs. The aim is to ensure reliability and reduce manual testing effort through repeatable, scalable automation.

### What you’ll accomplish
- Set up a machine for **Web UI** and **API** test automation.
- Understand project structure and configuration files.
- Run single tests or full suites with **TestNG**.
- Review **HTML reports** and **screenshots**.

---

## Prerequisite Knowledge
- **Java (OOP, classes, methods, collections)**
- **TestNG** (annotations, assertions, XML suite configs)
- **Selenium WebDriver** (locators, waits, actions)
- **REST APIs & RestAssured** (status codes, JSON/XML responses)
- **CLI** (run Java/Maven)
- **Git** (clone, pull, branch, commit, merge)

---

## Requirements
- **OS:** Windows (primary target)
- **Java:** 21
- **Maven:** 3.9.1
- **Selenium:** 4.35.0
- **TestNG:** 7.11.0
- **IDE:** Eclipse 2025‑06 or newer

> macOS is also supported for Java/Eclipse setup; browser drivers and paths may vary.

---

## Environment Setup

### 1) Install Java 21 (JDK)
**Windows**
1. Download from Oracle: https://www.oracle.com/java/technologies/downloads/#jdk21-windows
2. Install and set environment variables:
   - `JAVA_HOME = C:\Program Files\Java\jdk-21.x`
   - Add `%JAVA_HOME%\bin` to `Path`
3. Verify in Command Prompt: `java -version`

**macOS**
1. Download: https://www.oracle.com/java/technologies/downloads/#jdk21-mac  
2. Install `.pkg`, then verify in Terminal: `java -version`

### 2) Install Eclipse IDE (Java Developers)
- Download: https://www.eclipse.org/downloads/
- Install and select a workspace on first launch.

### 3) Install Maven
- Download: https://maven.apache.org/download.cgi
- Set `MAVEN_HOME` and add `%MAVEN_HOME%\bin` (Windows) or export on macOS.
- Verify: `mvn -v`

### 4) Create Maven Project & Add Dependencies
- In Eclipse: **File → New → Maven Project** → choose an archetype (e.g., `quickstart`).
- Replace/add the dependency block in your `pom.xml` with the **sample** below.

---

## Sample `pom.xml` — Dependencies Only
> This section includes **versions** as properties so you can manage them in one place.

```xml
<!-- pom.xml (dependencies section with version properties) -->
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>TestNG</groupId>
  <artifactId>AI4X_Automation</artifactId>
  <version>0.0.1-SNAPSHOT</version>
  <packaging>jar</packaging>
  <name>AI4X Automation</name>
  <url>http://maven.apache.org</url>
	<description>Automation Testing of AI4X Project</description>

  <properties>
		<project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
		<timestamp>${maven.build.timestamp}</timestamp>
		<maven.build.timestamp.format>yyyyMMdd-HHmm</maven.build.timestamp.format>
		<maven.compiler.source>21</maven.compiler.source>
		<maven.compiler.target>21</maven.compiler.target>
	</properties>

  <dependencies>

	<!-- WebDriver Manager Dependency -->
		<dependency>
			<groupId>io.github.bonigarcia</groupId>
			<artifactId>webdrivermanager</artifactId>
			<version>6.2.0</version>
		</dependency>

    <!-- Selenium WebDriver Dependency -->
		<dependency>
			<groupId>org.seleniumhq.selenium</groupId>
			<artifactId>selenium-java</artifactId>
			<version>4.35.0</version>
		</dependency>

		<dependency>
			<groupId>org.seleniumhq.selenium</groupId>
			<artifactId>selenium-support</artifactId>
			<version>4.35.0</version>
		</dependency>

		<dependency>
			<groupId>org.seleniumhq.selenium</groupId>
			<artifactId>selenium-chrome-driver</artifactId>
			<version>4.35.0</version>
		</dependency>
		
		<dependency>
    		<groupId>org.seleniumhq.selenium</groupId>
    		<artifactId>selenium-remote-driver</artifactId>
    		<version>4.35.0</version>
		</dependency>
		
		<!-- RestAssured -->
    	<dependency>
        	<groupId>io.rest-assured</groupId>
        	<artifactId>rest-assured</artifactId>
        	<version>5.5.6</version>
        	<scope>test</scope>
    	</dependency>
    
        <!-- JSON Assertion Support -->
    	<dependency>
        	<groupId>org.hamcrest</groupId>
        	<artifactId>hamcrest</artifactId>
        	<version>3.0</version>
    	</dependency>
    	
    	<dependency>
    		<groupId>org.json</groupId>
    		<artifactId>json</artifactId>
    		<version>20250517</version>
		</dependency>

    <!-- TestNG Dependency -->
		<dependency>
			<groupId>org.testng</groupId>
			<artifactId>testng</artifactId>
			<version>7.11.0</version>
			<scope>test</scope>
		</dependency>
    
  </dependencies>
</project>
```

> **Tip:** If you already manage versions via a corporate BOM, keep only the `<dependencies>` block and remove `<properties>`.

---

## Project Configuration

### Selenium Driver Options
- Supported browsers: **Chrome**, **Firefox**, **Edge**.
- Edit: `src/test/java/LibraryFiles/ReusableLibraryFile.java`
- Method: `OpenBrowserInstance`
- You can enable/disable arguments (e.g., `--incognito`) per browser.

### Global Test Settings
- File: `GlobalSettings.properties`
- Stores **URLs**, **usernames**, **passwords**, **target browser**.

### Test Data
- File: `testData/TestData.properties`
- Stores inputs used during flows (e.g., form values, language codes, etc.).

---

## Running Tests

### From Eclipse
- File: `src/test/java/TestCases/A_BaseSuiteFile.java`
- Each test has a `@Test` annotation.
- **Run a single test:** Click the **Run** icon near the method.
- **Run all tests:** Right‑click inside the file → **Run As → TestNG Test**.
- **Enable/Disable** a test: use `@Test(enabled = true|false)`.

---

## Screenshots
- Captured for **Web/UI** tests right before the driver quits.
- Location: `ScreenShots/`
- **Note:** API tests do **not** capture screenshots.

---

## HTML Reports
- Generated after each run as: `HtmlReport_[YYYY‑MM‑DD]_[HH‑mm‑ss].html`
- Location: `TestReports/`

---

## Summary
You now have a GitHub‑ready README with:
- Clear setup instructions for Java, Maven, Eclipse.
- A copy‑paste **Maven dependencies** block for Selenium, RestAssured, and TestNG.
- Steps to configure drivers, test data, and execute tests.
- Where to find screenshots and HTML reports.
