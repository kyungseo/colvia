# Installation and notifications

A Work acceptance records the person's decision about the exact result. It does
not commit, merge, publish, deploy, send a notification or accept another Work.
An explicit request can authorize notification as part of the same scope; do not
add a duplicate confirmation when the concrete receiver and action are already
covered. Use the managed Colvia receiver only, never a terminal notification as
substitute evidence. A displayed event is not a successful click or result acceptance.

## First connection

Use the installed manager in the account that will use Colvia. For an unconnected folder, use `connect-preview ROOT`. If it offers a Git choice, use the regular-folder preview for “later” or “just connect it.” For an explicit Git choice, request `connect-preview ROOT --init-git`. If Git needs registering, include `--git-executable ABSOLUTE_PATH` for the person's selected executable. Show the account-wide effect, executable identity, project folder, branch and affected files. Save the exact JSON privately and apply only the approved receipt. Cancel by leaving the preview unapplied. For an already-initialized repository use its normal connection preview. For a connected plain folder, keep the current Work accessible and explain the current limit before taking any Git action.

If an approved first connection is interrupted, use `connect-resume OPERATION` with the original ID. If the repository changed before connection files were prepared, explain the discrepancy. With the person’s agreement, use `connect-cancel OPERATION` to release the reservation and request a new preview. Any Git repository or account registration already created stays in place. Once connection files are prepared, continue the same operation; Colvia preserves unrelated staging. First connection does not stage, commit, create a remote or grant permission for those actions.

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
