package LibraryFiles;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.File;

public class GitAutomation 
{
	public static void main(String[] args) 
	{
		String repoPath = System.getProperty("user.dir");
		String branch = "";
		String commitMsg = "Updated commit message";

		// To push changes
		pushToGit(repoPath, branch, commitMsg);

		// To pull latest changes
		pullFromGit(repoPath, branch);
	}

	public static void pushToGit(String repoPath, String branchName, String commitMessage) 
	{
		try 
		{
			System.out.println("Pushing changes to Git...");

			runGitCommand("git add .", repoPath);
			runGitCommand("git commit -m \"" + commitMessage + "\"", repoPath);
			runGitCommand("git push origin " + branchName, repoPath);

			System.out.println("Code pushed to branch '" + branchName + "' successfully.");
		} 
		catch (Exception e) 
		{
			System.err.println("Push failed:");
			e.printStackTrace();
		}
	}

	public static void pullFromGit(String repoPath, String branchName) 
	{
		try 
		{
			System.out.println("Pulling latest changes from Git...");
			runGitCommand("git pull origin " + branchName, repoPath);
			System.out.println("Latest code pulled from branch '" + branchName + "' successfully.");
		} 
		catch (Exception e) 
		{
			System.err.println("Pull failed:");
			e.printStackTrace();
		}
	}

	private static void runGitCommand(String command, String repoPath) throws Exception {
		ProcessBuilder builder = new ProcessBuilder();
		boolean isWindows = System.getProperty("os.name").toLowerCase().contains("win");

		if (isWindows) 
		{
			builder.command("cmd.exe", "/c", command);
		} 
		else 
		{
			builder.command("bash", "-c", command);
		}

		builder.directory(new File(repoPath));
		builder.redirectErrorStream(true);

		Process process = builder.start();
		BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));

		String line;
		while ((line = reader.readLine()) != null) 
		{
			System.out.println(line);
		}

		int exitCode = process.waitFor();
		if (exitCode != 0) 
		{
			throw new RuntimeException("Command failed with exit code " + exitCode + ": " + command);
		}
	}
}
