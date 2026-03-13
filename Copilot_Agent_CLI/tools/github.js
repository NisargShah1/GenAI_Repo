import { Octokit } from "@octokit/rest";

/**
 * Instantiate Octokit with locally cached secrets (via ensureSecrets)
 */
const getOctokit = () => {
  // `ensureSecrets` loads the token from ~/.copilot-agent-secrets.json
  // and injects it into process.env before this is called.
  return new Octokit({
    auth: process.env.GITHUB_TOKEN
  });
};

/**
 * Fetch a Pull Request from GitHub API
 */
export async function getPullRequest(owner, repo, prNumber) {
  const octokit = getOctokit();
  const { data } = await octokit.pulls.get({
    owner,
    repo,
    pull_number: prNumber,
  });
  return data;
}

/**
 * List commits for a Pull Request
 */
export async function listCommits(owner, repo, prNumber) {
  const octokit = getOctokit();
  const { data } = await octokit.pulls.listCommits({
    owner,
    repo,
    pull_number: prNumber,
  });
  return data;
}

/**
 * Create a Pull Request via GitHub API
 */
export async function createPullRequest(owner, repo, title, head, base, body) {
  const octokit = getOctokit();
  const { data } = await octokit.pulls.create({
    owner,
    repo,
    title,
    head,
    base,
    body,
  });
  return data;
}

/**
 * Submit a Pull Request Review
 */
export async function reviewPullRequest(owner, repo, prNumber, reviewBody, event = "COMMENT") {
  const octokit = getOctokit();
  const { data } = await octokit.pulls.createReview({
    owner,
    repo,
    pull_number: prNumber,
    body: reviewBody,
    event,
  });
  return data;
}
