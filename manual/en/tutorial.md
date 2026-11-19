# Follow along with Colvia

[User guide](README.md) · [한국어](../ko/tutorial.md) · English

Install Colvia, connect a folder, and try writing a customer inquiry report or building a team to-do web app. In either exercise, you’ll agree on the scope, review a submission and its checks, and find the same task in a new chat.

[Install and connect](#install-and-connect) · [Customer inquiry report](#customer-inquiry-report) · [Team to-do web app](#team-to-do-web-app) · [What to try next](#what-to-try-next)

Stepping away before the first submission? Ask the agent to save your progress. In a new chat in the same folder, say “Pick up where we left off” to see the latest note and which files have changed since. [Using progress notes](work.md#progress-note)

## What you’ll use

| Part | What it does |
| --- | --- |
| You | Explain the goal, approve which files are in scope and how to check the result, then decide whether to accept the submission or ask for changes. |
| Codex or Claude Code | Reads your project material and rules, proposes a plan, edits files, runs checks, and submits the result through Colvia. |
| The project folder and Colvia | The folder holds your documents and code. The Colvia launcher helps the connected agent find its Work records. Colvia keeps approvals, submitted contents, and acceptance records in your device’s user data directory. |

Colvia records each task you scope and review as a **Work**. Granting file or command access in the app or CLI, approving the scope of a Work, and accepting the submission you reviewed are separate decisions.

## Install and connect

1. On macOS with Apple Silicon or Windows 11 on x64 or ARM64, open Codex or Claude Code and confirm you’re signed in. See the [platform and agent access requirements](reference.md#environments) for your setup.
2. Copy and run the command for your operating system from the [official installation page](https://colvia.github.io/downloads/#en). On Windows, open regular PowerShell from the Start menu as a standard user. Check the installed version when setup completes. [Installation and connection guide](install.md)
3. Create a local practice folder and open it in Codex or Claude Code. You can also connect an existing project. If your project uses Git, [ask the agent to register Git first](git.md#git-register) and connect the repository root. Ask:

   > Connect this folder to Colvia.

4. In the preview, check the folder, the files Colvia will add, and where it will store the records. Approve the connection if those details are right. If the app or CLI blocks access, [check the permissions it needs](install.md#access).
5. In the current chat, tell the agent what you want to do in a sentence or two. If you’ve already shared a goal, the agent can use it and your project rules to propose a plan. In an empty folder, you could start with “I’d like to make a team to-do app.”

Pick either exercise to start. If you try both, install Colvia once and connect a new folder for each exercise.

## Customer inquiry report

### Prepare the example files

Save these fictional customer inquiries as a UTF-8 file named `inquiries.csv` in the practice folder. Create `report.md` with the heading `# Weekly customer inquiry report`.

~~~csv
id,type,inquiry
Q01,Refund,When will the card reversal appear?
Q02,Refund,Where can I request a refund?
Q03,Refund,My cancellation was confirmed but the charge is still there.
Q04,Refund,Can I get a refund on an order placed with a coupon?
Q05,Refund,How can I check whether you received my refund request?
Q06,Shipping,My order has been preparing to ship for two days.
Q07,Shipping,When will I get another update about the delay?
Q08,Shipping,My tracking number still shows no results.
Q09,Shipping,The delivery estimate has passed. When will my order arrive?
Q10,Usage,How do I use my reward points?
Q11,Usage,Where can I find the receipt in my order history?
Q12,Other,What are your customer service hours?
~~~

### Approve the scope and review the result

1. In the connected folder, ask:

   > Turn these 12 inquiries into a one-page report for our weekly operations meeting. Include the count for each category, recurring questions, and two ways we could improve our guidance. We’ll decide priorities at the meeting.

   Check that the agent proposes reading `inquiries.csv` and editing only `report.md`. Review the file scope and the checks, then approve the plan if it looks right.

   > Go ahead with that scope. Keep the source inquiries intact and edit only report.md.

2. When the report is submitted for review, check the changed files and test results. Expect 5 refund, 4 shipping, 2 usage, and 1 other inquiry, for a total of 12.
3. Open the same project in a new chat and ask the question below. If several Works have similar titles, select this report.

   > Show me what I need to review in the weekly inquiry report. Which files changed, and what decision do you need from me?

4. Read the result and request a change within the approved scope.

   > Add that when a delay continues, we should tell the customer when to expect the next update. Change only report.md and wait for me to review the difference before submitting again.

   Ask, “Show me just the sentences that differ from the last submission.” Ask the agent to submit again after you’ve reviewed the changes. If the new submission looks right, say “I accept this submission.” Check that Colvia recorded the accepted submission and that the original CSV is still there.

If Colvia blocks a submission, ask which file caused it and why. Existing edits stay in the work folder. Review and resolve the changes before submitting again. Ask for a [scope preview](work.md#scope-change) before touching additional files. If a file has already changed, inspect the edit and decide whether to keep it separately or restore it yourself before requesting a new preview. [Guidance for reviewing and revising work](work.md#review)

## Team to-do web app

### Decide what goes into the first version

Connect a separate empty folder and describe what you want to do.

> After meetings, our action items get scattered across chats. I’d like a small web app where our four operations team members can see who owns each task and whether it’s done.

If the agent asks where you’ll run it and how you’ll check it, try:

> One shared list is enough for the first version. Use fictional data. I’ll check it in two browser tabs on this laptop. Save account sign-in for later.

The agent might propose a small Node.js server and a browser page. If you choose Node.js, check the environment with `node --version` and `npm --version`. Ask the agent to record the run and test commands and the browser address in the project README.

Check the plan for the server, browser page, list storage, test files, and completion criteria. If it fits the first version you want, approve the scope and ask the agent to build it. If the web app needs updated setup instructions and a new configuration file, ask for one scope preview before the first submission. Review the paths, reason and checks, then approve both and review them with the app.

### Run the app and review the result

1. Run the app using the commands in its project README. Open the same address in two browser tabs. In the first tab, add “Draft refund guidance” and “Update shipping delay policy.”
2. Refresh the second tab and check that both items appear. Assign someone to a task and mark an item complete. Refresh the first tab and check that it shows the same state. Restart the server and check that the list and completion status survive.
3. Ask the agent to record which checks it ran and what it couldn’t confirm in the submission. This exercise checks that two tabs on the same computer share a list.
4. Open the same project in a new chat and ask, “Show me the last submission for the to-do app, the checks that ran, and what I need to decide.” Review the result, say “I accept this first version” if it’s ready, and confirm that acceptance was recorded. To save a next step, try “I’d like to hide completed tasks from the list.” [Find a recorded next step](work.md#follow-up)

## What to try next

- **Try a notification for the report.** After preparing the report above and before submitting it for review, ask, “The draft is ready. Submit it for review and notify me on this device.” One submission covers the request when the agent handles the submission and notification. If prompted, grant notification permission yourself. Open the result from the notification and read the submission before accepting it or asking for changes. If delivery is uncertain, check the existing notification record first. If you miss the notification or it doesn’t open the result, ask in the same project, “Is anything waiting for my review?” [Set up notifications and check delivery](maintenance.md#notifications)
- **Pick up with another agent.** If you use both Codex and Claude Code, open the same project with the other agent and find the Work. That agent needs access to the project folder and the Colvia records.
- **Put an accepted result into Git.** If your project uses Git, review the changes to commit and the current staging area, then approve the integration separately. [Git integration guide](git.md#git-integration)
- **Back up the records.** Back up your project files and Colvia records separately. [Back up and restore records](records.md#backup)
- **Find help for your next step.** [Set up notifications](maintenance.md#notifications) · [Updates and recovery](maintenance.md#update) · [Continue after a folder move](records.md#move) · [Disconnect a project](maintenance.md#disconnect)

### When demonstrating the exercises

Use fictional data and say when you’re showing a submission or app screen prepared in advance. For a walkthrough from scratch, show installation, connection, scope approval, check results, lookup in a new chat, and acceptance.
