# Complete Your First Work

[Previous: preparation](getting-started.md) · [Contents](README.md) · [한국어](../ko/first-work.md) · [Next: resume](resume.md)

A Work keeps the agreed task, result and acceptance connected. You explain the desired result; the agent prepares the exact records and performs the authorized work. You decide the scope and result acceptance.

## Agree On A Small Result

For a document task, ask:

> Improve this README's installation section. Preserve the rest, including existing quotes, links and examples. Explain the proposed changes and how you will check them before editing.

The agent reads project instructions, `./colvia view --details` and the current adapter, then identifies the existing plan, affected files, expected result, checks, limits and stop conditions. It resolves material gaps and prepares the exact intent for your decision. An existing applicable approval carries forward; a changed scope or consumed approval follows its contract. See [Guided Intent](../../docs/GUIDED-INTENT-FORMATION.md).

## Implement And Check

After the exact scope is accepted, the agent establishes the Work baseline and edits within that scope. For this example, verify the requested installation guidance, preserved text outside the section, links and formatting. Keep temporary test data outside the Work's tracked content unless it belongs to the accepted result. Missing or unavailable checks stay visible.

The agent records the result and presents what changed, what was checked and any remaining limits. It prepares the result confirmation and reads the same revision with `./colvia view work WORK_ID --revision REVISION_ID`. The agent substitutes the actual ID and prepares canonical input; you can review the explanation and confirmation without editing JSON. [General Work](../../docs/GENERAL-WORK.md) defines the record fields and acceptance rules.

## Decide And Continue

When the result meets the agreed criteria, accept the exact result shown. The agent applies that ticket and checks the stored state and current files. Passing tests or a reviewer recommendation support your decision; the acceptance is yours. In local work, the edited files already exist in the control checkout. Worker results have their own exact application procedure.

The completion report should say what was achieved, what remains in the project plan and the recommended next step with its reason. A recommendation can be to finish here. If there is no selected follow-up, say so and explain what decision would be useful. A recommendation does not start another task.

## Preserve The Result

Keep the accepted records, necessary source and recovery inputs. Ask for Git status and the proposed preservation set before deciding on a commit or push. Review important ignored outputs separately. Clean up only when ownership, remaining use and recoverability are established. Work acceptance, Git integration and remote publication remain separate decisions.

If application stops or current files differ from the result, preserve the inputs and inspect the supported recovery path. Continue with [a fresh conversation](resume.md) using the project records rather than reconstructing authority from chat history.

The older checkout-1 exercise's recorded observations remain historical. New distribution, agent behavior and real-project quality need their own evidence.
