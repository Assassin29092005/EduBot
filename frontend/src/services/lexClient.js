import { LexRuntimeV2Client, RecognizeTextCommand } from '@aws-sdk/client-lex-runtime-v2';
import { fromCognitoIdentityPool } from '@aws-sdk/credential-providers';

const REGION = process.env.REACT_APP_AWS_REGION || 'us-east-1';
const IDENTITY_POOL_ID = process.env.REACT_APP_IDENTITY_POOL_ID;
const BOT_ID = process.env.REACT_APP_LEX_BOT_ID;
const BOT_ALIAS_ID = process.env.REACT_APP_LEX_BOT_ALIAS_ID;
const LOCALE_ID = 'en_US';

const client = new LexRuntimeV2Client({
  region: REGION,
  credentials: fromCognitoIdentityPool({
    clientConfig: { region: REGION },
    identityPoolId: IDENTITY_POOL_ID,
  }),
});

// Generate a unique session ID per browser session
const SESSION_ID = `session-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

export async function sendMessage(text) {
  const command = new RecognizeTextCommand({
    botId: BOT_ID,
    botAliasId: BOT_ALIAS_ID,
    localeId: LOCALE_ID,
    sessionId: SESSION_ID,
    text: text,
  });

  const response = await client.send(command);

  const messages = response.messages || [];
  if (messages.length > 0) {
    return messages.map((m) => m.content).join('\n');
  }
  return "I'm sorry, I didn't get a response. Please try again.";
}
