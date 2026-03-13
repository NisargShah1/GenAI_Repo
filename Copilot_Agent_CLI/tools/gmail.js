import { google } from 'googleapis';

/**
 * Instantiate Gmail client with locally cached secrets
 */
const getGmailClient = () => {
  const clientId = process.env.GMAIL_CLIENT_ID;
  const clientSecret = process.env.GMAIL_CLIENT_SECRET;
  const refreshToken = process.env.GMAIL_REFRESH_TOKEN;

  if (!clientId || !clientSecret || !refreshToken) {
    throw new Error("Missing Gmail OAuth credentials in ~/.copilot-agent-secrets.json. Need GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, and GMAIL_REFRESH_TOKEN.");
  }

  const oAuth2Client = new google.auth.OAuth2(clientId, clientSecret, "urn:ietf:wg:oauth:2.0:oob");
  oAuth2Client.setCredentials({ refresh_token: refreshToken });

  return google.gmail({ version: 'v1', auth: oAuth2Client });
};

/**
 * Fetch recent unread emails
 */
export async function fetchUnreadEmails(maxResults = 10) {
  const gmail = getGmailClient();
  const res = await gmail.users.messages.list({
    userId: 'me',
    q: 'is:unread',
    maxResults
  });

  const messages = res.data.messages || [];
  const emails = [];

  for (const msg of messages) {
    const emailData = await gmail.users.messages.get({
      userId: 'me',
      id: msg.id,
      format: 'full'
    });
    emails.push(emailData.data);
  }

  return emails;
}

/**
 * Apply labels to an email (e.g., Add 'Review Required', remove 'UNREAD')
 */
export async function applyLabel(messageId, labelIdsToAdd = [], labelIdsToRemove = []) {
  const gmail = getGmailClient();
  const res = await gmail.users.messages.modify({
    userId: 'me',
    id: messageId,
    requestBody: {
      addLabelIds: labelIdsToAdd,
      removeLabelIds: labelIdsToRemove
    }
  });
  return res.data;
}

/**
 * Create a draft reply for a specific thread
 */
export async function createDraft(threadId, to, subject, bodyText) {
  const gmail = getGmailClient();

  const rawMessage = [
    `To: ${to}`,
    `Subject: Re: ${subject}`,
    '',
    bodyText
  ].join('\n');

  // Base64url encode the message
  const encodedMessage = Buffer.from(rawMessage)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');

  const res = await gmail.users.drafts.create({
    userId: 'me',
    requestBody: {
      message: {
        raw: encodedMessage,
        threadId: threadId
      }
    }
  });

  return res.data;
}

/**
 * Send an existing draft (Requires explicit human review prior to calling)
 */
export async function sendDraft(draftId) {
  const gmail = getGmailClient();
  const res = await gmail.users.drafts.send({
    userId: 'me',
    requestBody: {
      id: draftId
    }
  });
  return res.data;
}
