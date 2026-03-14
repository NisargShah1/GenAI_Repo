import { google } from 'googleapis';

/**
 * Initialize and return an authenticated Gmail client using OAuth2.
 * Requires GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, and GMAIL_REFRESH_TOKEN in process.env.
 */
function getGmailClient() {
  const oAuth2Client = new google.auth.OAuth2(
    process.env.GMAIL_CLIENT_ID,
    process.env.GMAIL_CLIENT_SECRET
  );
  oAuth2Client.setCredentials({ refresh_token: process.env.GMAIL_REFRESH_TOKEN });
  return google.gmail({ version: 'v1', auth: oAuth2Client });
}

/**
 * Fetch a specified number of unread emails.
 */
export async function fetchUnreadEmails(maxResults = 5) {
  console.log(`📧 [Gmail] Fetching up to ${maxResults} unread emails...`);
  try {
    const gmail = getGmailClient();
    const res = await gmail.users.messages.list({
      userId: 'me',
      q: 'is:unread',
      maxResults
    });

    const messages = res.data.messages;
    if (!messages || messages.length === 0) {
      return 'No unread emails found.';
    }

    const emails = [];
    for (const m of messages) {
      const msg = await gmail.users.messages.get({ 
        userId: 'me', 
        id: m.id, 
        format: 'full' // Fetch full so we get body and snippet
      });
      
      const payload = msg.data.payload;
      const headers = payload.headers;
      const subject = headers.find(h => h.name === 'Subject')?.value || 'No Subject';
      const from = headers.find(h => h.name === 'From')?.value || 'Unknown Sender';
      const date = headers.find(h => h.name === 'Date')?.value || '';
      
      // Attempt to decode body (text/plain)
      let bodyData = '';
      if (payload.parts && payload.parts.length > 0) {
        const part = payload.parts.find(p => p.mimeType === 'text/plain') || payload.parts[0];
        if (part.body && part.body.data) {
          bodyData = Buffer.from(part.body.data, 'base64').toString('utf-8');
        }
      } else if (payload.body && payload.body.data) {
        bodyData = Buffer.from(payload.body.data, 'base64').toString('utf-8');
      }

      emails.push({ 
        id: m.id, 
        from, 
        subject, 
        date, 
        snippet: msg.data.snippet,
        body: bodyData.substring(0, 1000) // Truncate to save tokens
      });
    }

    return JSON.stringify(emails, null, 2);
  } catch (error) {
    throw new Error(`fetchUnreadEmails failed: ${error.message}`);
  }
}

/**
 * List available labels (to get label IDs for applying/removing).
 */
export async function listLabels() {
  console.log(`🗂️ [Gmail] Listing available labels...`);
  try {
    const gmail = getGmailClient();
    const res = await gmail.users.labels.list({ userId: 'me' });
    const labels = res.data.labels.map(l => ({ id: l.id, name: l.name }));
    return JSON.stringify(labels, null, 2);
  } catch (error) {
    throw new Error(`listLabels failed: ${error.message}`);
  }
}

/**
 * Apply or remove labels from an email.
 * Standard label IDs include: 'UNREAD', 'INBOX', 'TRASH', 'SPAM'.
 */
export async function applyLabel(messageId, addLabelIds = [], removeLabelIds = []) {
  console.log(`🏷️ [Gmail] Modifying labels for message ${messageId}...`);
  try {
    const gmail = getGmailClient();
    
    // Ensure they are arrays
    const add = Array.isArray(addLabelIds) ? addLabelIds : (addLabelIds ? [addLabelIds] : []);
    const remove = Array.isArray(removeLabelIds) ? removeLabelIds : (removeLabelIds ? [removeLabelIds] : []);

    await gmail.users.messages.modify({
      userId: 'me',
      id: messageId,
      requestBody: {
        addLabelIds: add,
        removeLabelIds: remove
      }
    });

    return `Successfully modified labels for message ${messageId}.`;
  } catch (error) {
    throw new Error(`applyLabel failed: ${error.message}`);
  }
}

/**
 * Helper to construct a raw base64 encoded MIME email message.
 */
function makeRawEmail(to, subject, body) {
  const str = [
    `To: ${to}`,
    `Subject: ${subject}`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=utf-8',
    '',
    body
  ].join('\n');
  return Buffer.from(str).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/**
 * Create a draft email reply.
 */
export async function createDraft(to, subject, body) {
  console.log(`📝 [Gmail] Creating draft email to ${to}...`);
  try {
    const gmail = getGmailClient();
    const raw = makeRawEmail(to, subject, body);

    const res = await gmail.users.drafts.create({
      userId: 'me',
      requestBody: {
        message: { raw }
      }
    });

    return `Successfully created draft with ID: ${res.data.id}`;
  } catch (error) {
    throw new Error(`createDraft failed: ${error.message}`);
  }
}

/**
 * Send an existing draft.
 */
export async function sendDraft(draftId) {
  console.log(`🚀 [Gmail] Sending draft ${draftId}...`);
  try {
    const gmail = getGmailClient();

    const res = await gmail.users.drafts.send({
      userId: 'me',
      requestBody: {
        id: draftId
      }
    });

    return `Successfully sent draft. Sent Message ID: ${res.data.id}`;
  } catch (error) {
    throw new Error(`sendDraft failed: ${error.message}`);
  }
}
