# Delivery

How a change travels from a branch to a merged pull request. People decide; the pipeline
proves.

- DEL-1. Work happens on `feat/<id-lower>-<short-name>`, branched from an up-to-date `main`.
  Commit messages are `<ID>: <what changed>`. A spec, its tests and its code travel together.
- DEL-2. Nobody commits to `main` directly. Merging is a person's decision, after review.
  Agents never approve, force-push or delete branches they didn't create.
- DEL-3. Gates before a pull request, in order:
  1. `standards/checks/all.sh` passes (spec format, traceability, approved libraries,
     Dockerfiles, style and code security).
  2. Both test suites pass against the app running locally.
  3. Everything is committed.
  4. All tests pass in the branch's own GKE sandbox, for that exact commit.
- DEL-4. The pull request follows `.github/pull_request_template.md`: the spec, `Closes #<issue>`,
  the criteria covered and the sandbox result. CI then repeats every check independently, in
  a fresh PR sandbox. A person reviews the spec diff first, then the tests, then the code.
- DEL-5. Issues, comments and pull requests are shown to the person before they are posted.
- DEL-6. Environments, and who deploys to them:

  | Environment | Deployed by | Test-only endpoints |
  |---|---|---|
  | Local | the developer or agent | on |
  | Dev sandbox (GKE, per branch) | the agent, before the PR | on |
  | PR sandbox (GKE, per PR) | CI, on every push | on |
  | UAT (Cloud Run) | CI, on every merge to `main` | off |
  | Production (GKE) | the release workflow, after UAT (REL-3) | off |

  Agents never deploy to UAT or production themselves.
- DEL-7. Sandboxes are temporary: a PR sandbox is deleted when its PR closes, and a dev sandbox
  when its owner is done, or after 24 hours at the latest.
