# EduBot — AWS Serverless Student Assistant Chatbot

## Project Overview

EduBot is a cloud-native, fully serverless chatbot that helps students query academic information (syllabi, schedules, professor info, assignment deadlines). The project demonstrates end-to-end cloud application development: frontend, backend API, database, CI/CD automation, and monitoring.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Actions CI/CD                     │
│            (SAM build → test → deploy on every push)            │
└──────────────────────────────┬──────────────────────────────────┘
                               │ deploys
                               ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│  S3 + CF     │    │ Amazon       │    │ CloudWatch       │
│  Static Site │    │ Cognito      │    │ Dashboards +     │
│  (React UI)  │──▶│ Identity Pool│    │ X-Ray Tracing    │
└──────┬───────┘    └──────┬───────┘    └──────────────────┘
       │                   │                      ▲
       │ chat messages     │ auth                  │ logs/metrics
       ▼                   ▼                      │
┌──────────────────────────────────┐              │
│         Amazon Lex v2            │              │
│    (NLP — intent detection)      │              │
└──────────────┬───────────────────┘              │
               │ invokes                          │
               ▼                                  │
┌──────────────────────────────────┐              │
│         AWS Lambda               │──────────────┘
│    (Python 3.12 — business logic)│
└──────────────┬───────────────────┘
               │ queries
               ▼
┌──────────────────────────────────┐
│       Amazon DynamoDB            │
│    (Courses table — key-value)   │
└──────────────────────────────────┘
```

### AWS Services Used (7 total)
1. **S3 + CloudFront** — static website hosting for React frontend
2. **Amazon Cognito** — unauthenticated identity pool for browser → Lex access
3. **Amazon Lex v2** — NLP engine for intent detection and slot extraction
4. **AWS Lambda** — serverless backend logic (Python 3.12)
5. **Amazon DynamoDB** — NoSQL database for course data
6. **CloudWatch** — logging, metrics dashboards, alarms
7. **X-Ray** — distributed tracing across Lambda + DynamoDB

### CI/CD
- **GitHub Actions** workflow triggers on push to `main`
- Uses **AWS SAM** (Serverless Application Model) to define all infrastructure as code
- Pipeline: install → build → test → sam deploy

---

## Project Structure

```
edubot-cloud/
├── CLAUDE.md                    # This file — project instructions
├── README.md                    # Project documentation for submission
├── template.yaml                # AWS SAM template (all infrastructure)
├── samconfig.toml               # SAM deployment config
│
├── frontend/                    # React chat UI
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── index.js
│       ├── App.js               # Main app component
│       ├── App.css
│       ├── components/
│       │   ├── ChatWindow.js    # Chat message display
│       │   ├── ChatInput.js     # User input box
│       │   └── MessageBubble.js # Individual message bubble
│       └── services/
│           └── lexClient.js     # AWS SDK Lex runtime client
│
├── backend/
│   └── lambda/
│       ├── handler.py           # Lambda function code
│       ├── requirements.txt     # Python dependencies (boto3)
│       └── seed_data.py         # Script to populate DynamoDB with sample data
│
├── monitoring/
│   └── dashboard.json           # CloudWatch dashboard definition
│
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Actions CI/CD pipeline
│
├── docs/
│   └── architecture.png         # Architecture diagram for report
│
└── tests/
    └── test_handler.py          # Unit tests for Lambda function
```

---

## Implementation Plan — Execute in Order

### Phase 1: SAM Template (Infrastructure as Code)

Create `template.yaml` — this is the most critical file. It defines ALL AWS resources:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: EduBot — Serverless Student Assistant Chatbot

Globals:
  Function:
    Timeout: 10
    Runtime: python3.12
    Tracing: Active  # enables X-Ray

Resources:
  # DynamoDB Table
  CoursesTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: EduBot-Courses
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: course_id
          AttributeType: S
      KeySchema:
        - AttributeName: course_id
          KeyType: HASH

  # Lambda Function
  EduBotFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: EduBotHandler
      CodeUri: backend/lambda/
      Handler: handler.lambda_handler
      MemorySize: 128
      Environment:
        Variables:
          TABLE_NAME: !Ref CoursesTable
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref CoursesTable
        - CloudWatchLogsFullAccess

  # Lambda Permission for Lex
  LexInvokePermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref EduBotFunction
      Action: lambda:InvokeFunction
      Principal: lexv2.amazonaws.com

  # S3 Bucket for Frontend
  FrontendBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'edubot-frontend-${AWS::AccountId}'
      WebsiteConfiguration:
        IndexDocument: index.html
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false

  FrontendBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref FrontendBucket
      PolicyDocument:
        Statement:
          - Sid: PublicRead
            Effect: Allow
            Principal: '*'
            Action: s3:GetObject
            Resource: !Sub '${FrontendBucket.Arn}/*'

  # Cognito Identity Pool (unauthenticated access to Lex)
  EduBotIdentityPool:
    Type: AWS::Cognito::IdentityPool
    Properties:
      IdentityPoolName: EduBotIdentityPool
      AllowUnauthenticatedIdentities: true

  # IAM Role for unauthenticated Cognito users
  CognitoUnauthRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Federated: cognito-identity.amazonaws.com
            Action: sts:AssumeRoleWithWebIdentity
            Condition:
              StringEquals:
                cognito-identity.amazonaws.com:aud: !Ref EduBotIdentityPool
              ForAnyValue:StringLike:
                cognito-identity.amazonaws.com:amr: unauthenticated
      Policies:
        - PolicyName: LexAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - lex:RecognizeText
                  - lex:DeleteSession
                  - lex:PutSession
                Resource: '*'

  CognitoRoleAttachment:
    Type: AWS::Cognito::IdentityPoolRoleAttachment
    Properties:
      IdentityPoolId: !Ref EduBotIdentityPool
      Roles:
        unauthenticated: !GetAtt CognitoUnauthRole.Arn

Outputs:
  FrontendURL:
    Value: !GetAtt FrontendBucket.WebsiteURL
  IdentityPoolId:
    Value: !Ref EduBotIdentityPool
  LambdaFunctionArn:
    Value: !GetAtt EduBotFunction.Arn
  CoursesTableName:
    Value: !Ref CoursesTable
```

**Notes on SAM template:**
- Lex v2 bot itself is NOT in the SAM template because CloudFormation support for Lex v2 bots is complex and fragile. The bot is created manually once, then referenced by bot ID in the frontend config. This is standard practice.
- Everything else (Lambda, DynamoDB, S3, Cognito, IAM) is fully automated.

### Phase 2: Lambda Function

Create `backend/lambda/handler.py`:
- Read TABLE_NAME from environment variable (not hardcoded)
- Support 5 intents: GetCourseSyllabus, GetProfessorInfo, GetClassSchedule, GetAssignmentDeadline, FallbackIntent
- Include proper error handling and logging
- Use X-Ray tracing with `aws_xray_sdk` if available, graceful fallback if not

Create `backend/lambda/seed_data.py`:
- Standalone script to populate DynamoDB with 6-8 courses (not just 3)
- Include varied data: different departments, schedules, professors
- Run locally with `python seed_data.py` after deployment

Create `backend/lambda/requirements.txt`:
- boto3 (bundled in Lambda runtime, but declare it)

### Phase 3: React Frontend

Create a React app in `frontend/`:

**Key components:**
1. `lexClient.js` — initializes AWS SDK v3 LexRuntimeV2Client with Cognito credentials
   - Uses `@aws-sdk/client-lex-runtime-v2`
   - Uses `@aws-sdk/credential-providers` (fromCognitoIdentityPool)
   - Config values (region, identityPoolId, botId, botAliasId) from environment variables

2. `ChatWindow.js` — scrollable message list, auto-scroll to bottom
3. `ChatInput.js` — text input with send button, enter-to-send
4. `MessageBubble.js` — styled differently for user vs bot messages
5. `App.js` — main layout with header ("EduBot — Student Assistant"), chat area

**Styling:**
- Clean, modern chat UI
- University/academic theme (blue/white color scheme)
- Mobile-responsive
- Loading indicator while waiting for Lex response

**Environment variables** (in `.env` file, NOT committed to git):
```
REACT_APP_AWS_REGION=us-east-1
REACT_APP_IDENTITY_POOL_ID=<from SAM output>
REACT_APP_LEX_BOT_ID=<from Lex console>
REACT_APP_LEX_BOT_ALIAS_ID=<from Lex console>
```

### Phase 4: Unit Tests

Create `tests/test_handler.py`:
- Test each intent with mock Lex event payloads
- Test missing slot handling (should return ElicitSlot)
- Test course not found scenario
- Test fallback intent
- Use `unittest` with `unittest.mock` to mock DynamoDB

### Phase 5: CI/CD Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy EduBot

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run tests
        run: |
          pip install boto3 moto
          python -m pytest tests/ -v

      - uses: aws-actions/setup-sam@v2
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: SAM Build
        run: sam build

      - name: SAM Deploy
        run: sam deploy --no-confirm-changeset --no-fail-on-empty-changeset

  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install & Build Frontend
        working-directory: frontend
        run: |
          npm ci
          npm run build
        env:
          REACT_APP_AWS_REGION: us-east-1
          REACT_APP_IDENTITY_POOL_ID: ${{ secrets.IDENTITY_POOL_ID }}
          REACT_APP_LEX_BOT_ID: ${{ secrets.LEX_BOT_ID }}
          REACT_APP_LEX_BOT_ALIAS_ID: ${{ secrets.LEX_BOT_ALIAS_ID }}

      - name: Deploy to S3
        run: |
          aws s3 sync frontend/build/ s3://edubot-frontend-${{ secrets.AWS_ACCOUNT_ID }}/ --delete
```

### Phase 6: Monitoring

Create `monitoring/dashboard.json`:
- CloudWatch dashboard with widgets for:
  - Lambda invocation count (line chart)
  - Lambda errors (line chart)
  - Lambda duration p50/p90/p99 (line chart)
  - DynamoDB consumed read capacity (line chart)
  - Lex conversation count (number widget)
- Can be deployed via AWS CLI: `aws cloudwatch put-dashboard`

### Phase 7: Documentation

Create `README.md` with:
1. Project overview and purpose
2. Architecture diagram (embed the image from docs/)
3. AWS services used — explain WHY each service was chosen
4. Prerequisites (AWS account, Node.js, Python, SAM CLI, GitHub)
5. Local development setup
6. Deployment steps (both manual first-time and CI/CD)
7. How to use the chatbot
8. Monitoring and observability
9. Cost analysis (free tier breakdown)
10. Future enhancements

---

## Important Implementation Details

### Region
Use `us-east-1` throughout — Lex v2 availability is best there.

### Lex Bot (Manual Step)
The Lex v2 bot must be created manually via the AWS console because:
- CloudFormation support for Lex v2 is incomplete
- Bot training/building is an interactive process
- This is standard practice even in production

After creating the bot manually:
1. Note the Bot ID and Bot Alias ID
2. Add them as GitHub secrets for CI/CD
3. Add them to the frontend .env file for local dev

### Naming Conventions
- SAM stack name: `edubot-stack`
- All resource names prefixed with `EduBot-` or `edubot-`
- Use kebab-case for S3 buckets, PascalCase for CloudFormation resources

### Security
- Never commit AWS credentials or .env files
- Use least-privilege IAM roles
- Cognito allows only Lex access, nothing else
- S3 bucket is public-read only (static site hosting requires it)

---

## Commands Reference

```bash
# Local development
cd frontend && npm start              # Start React dev server
sam build                              # Build SAM template
sam local invoke EduBotFunction        # Test Lambda locally
sam deploy --guided                    # First-time deployment (interactive)
sam deploy                             # Subsequent deployments

# Seed database
cd backend/lambda && python seed_data.py

# Run tests
python -m pytest tests/ -v

# Deploy frontend manually
cd frontend && npm run build
aws s3 sync build/ s3://edubot-frontend-<account-id>/ --delete

# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name EduBot-Dashboard \
  --dashboard-body file://monitoring/dashboard.json
```