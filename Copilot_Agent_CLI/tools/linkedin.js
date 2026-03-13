/**
 * Helper to get the LinkedIn person URN required for publishing.
 * It uses the OpenID Connect userinfo endpoint.
 */
async function getLinkedInUrn(accessToken) {
  const response = await fetch('https://api.linkedin.com/v2/userinfo', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch LinkedIn User Info: ${response.statusText}`);
  }

  const data = await response.json();
  // `sub` is the unique member ID
  return `urn:li:person:${data.sub}`;
}

/**
 * Publishes a text post to the authenticated user's LinkedIn profile.
 * Requires LINKEDIN_ACCESS_TOKEN in ~/.copilot-agent-secrets.json or process.env
 * @param {string} text - The content of the LinkedIn post.
 */
export async function publishLinkedInPost(text) {
  const accessToken = process.env.LINKEDIN_ACCESS_TOKEN;
  
  if (!accessToken) {
    throw new Error("Missing LINKEDIN_ACCESS_TOKEN. Please provide it via local secrets.");
  }

  console.log(`\n🔗 [LinkedIn] Fetching user profile URN...`);
  const authorUrn = await getLinkedInUrn(accessToken);

  console.log(`🔗 [LinkedIn] Publishing post to profile: ${authorUrn}`);
  
  const payload = {
    author: authorUrn,
    lifecycleState: "PUBLISHED",
    specificContent: {
      "com.linkedin.ugc.ShareContent": {
        shareCommentary: {
          text: text
        },
        shareMediaCategory: "NONE"
      }
    },
    visibility: {
      "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
  };

  const response = await fetch('https://api.linkedin.com/v2/ugcPosts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
      'X-Restli-Protocol-Version': '2.0.0'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Failed to publish LinkedIn post: ${response.status} - ${errorBody}`);
  }

  const result = await response.json();
  return `Successfully published to LinkedIn! Post ID: ${result.id}`;
}
