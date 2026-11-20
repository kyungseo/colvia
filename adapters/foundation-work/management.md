# Installation and notifications

A Work acceptance records the person's decision about the exact result. It does
not commit, merge, publish, deploy, send a notification or accept another Work.
An explicit request can authorize notification as part of the same scope; do not
add a duplicate confirmation when the concrete receiver and action are already
covered. Use the managed Colvia receiver only, never a terminal notification as
substitute evidence. A displayed event is not a successful click or result acceptance.

## First connection

Use the installed manager in the account that will use Colvia. For an unconnected folder, use `connect-preview ROOT`. If it offers a Git choice, use the regular-folder preview for “later” or “just connect it.” For an explicit Git choice, request `connect-preview ROOT --init-git`. If Git needs registering, include `--git-executable ABSOLUTE_PATH` for the person's selected executable. Show the account-wide effect, executable identity, project folder, branch and affected files. Save the exact JSON privately and apply only the approved receipt. Cancel by leaving the preview unapplied. Use the ordinary Git connection preview for an unconnected repository. For a folder already connected to Colvia, use the conversion below.

If an approved first connection is interrupted, use `connect-resume OPERATION` with the original ID. If the repository changed before connection files were prepared, explain the discrepancy. With the person’s agreement, use `connect-cancel OPERATION` to release the reservation and request a new preview. Any Git repository or account registration already created stays in place. Once connection files are prepared, continue the same operation; Colvia preserves unrelated staging. First connection does not stage, commit, create a remote or grant permission for those actions.

## Start using Git in a connected folder

For “I'd like to manage this folder with Git,” run the installed manager's `git-transition-preview ROOT` on the connected folder, including when the person has already run `git init`. Use the existing account Git registration or offer its separate registration preview first. Explain whether Colvia will initialize a local repository or keep the existing one, and that the same project, Work history, files and staging are retained. An unfinished or paused Work or a pending effect blocks conversion. Never discard a Work to clear that condition without a separate user decision. After external initialization, keep the original folder and markers in place. Use the project launcher with `--finish-plain-work ordinary list`. In this mode use existing Work view, review or content and offer `backup export` with both paths outside the project. For an already approved Work use start, or explicitly resume a paused Work, then submit under the existing scope. Review and request changes or accept the exact result. For discard show the lifecycle preview, obtain the person's decision, and apply its receipt. A planned Work can be inspected or explicitly discarded. Do not widen scope, start a new Work or imply consent to convert. Once all Work is terminal, obtain a fresh conversion preview.

Capture the JSON preview in a private file. Only after approval apply that plan, receipt, statement and a fresh operation ID with `git-transition-apply`. After interruption, use `git-transition-resume OPERATION`. If files or the Git index changed, use `git-transition-resume-preview OPERATION`, explain what will be preserved, and pass the new receipt and statement only after the person confirms. If another program initialized Git before Colvia published any project change, ask before using `git-transition-cancel OPERATION` to release only this reservation. Then preview adoption of the existing repository. Never reinitialize, reset staging, create a commit or configure a remote as part of conversion.

## Managed setup and notifications

Use `./colvia manage --help` for the manager bound to this same installation;
`./colvia --json manage status` does not open a Work or change settings. Never
supply a different management root to bypass a refusal. On Windows use the
project's `colvia.cmd` launcher with the same arguments. Installation, OS consent
and subscription login are separate from approving a Work.

For an explicitly requested result notification, first inspect
`./colvia --json manage notice-check`. If registration is needed, use the same
manager's `notice-enable` only within authorization; OS consent may require the
person. Use the returned receiver identity in `delivery prepare --step submit`
with the exact Work, prepared summary and check results. Record the already-given
scope approval with `delivery start`, then `delivery run`. This replaces the
ordinary submit for that result; do not submit twice. After the delivery finishes,
`delivery notify DELIVERY_ID` resolves this project's record location and calls
the managed receiver once. An unknown emission is not permission to repeat it.
Use `delivery view` or `delivery details` to find the retained result. Neither
notification nor clicking it accepts the Work. No desktop or OS qualification
may be inferred from these commands being present.

For an interrupted update, read `guide recovery`.
