#!/bin/sh

BASE_URL="http://127.0.0.1:3001"
EMAIL="admin@example.com"
PASSWORD="yourpassword"

# ─────────────────────────────────────────
# Configuration — Edit these values
# ─────────────────────────────────────────
KNOWLEDGE_NAME="RAG-KB"
KNOWLEDGE_DESC="Auto-created on startup"
MODEL_ID="model-with-kb"
MODEL_NAME="Model with knowledge"
BASE_MODEL="/app/model/"
MODEL_DESC="Custom model with knowledge base"
FILES_DIR="./rag-files"


if sudo docker compose -f docker-compose-vllm-RAG-update.yml up -d; then
    echo "Docker image built successfully and container running successfully."
else
    echo "Failed to build Docker image or to run Docker container."
    exit 1
fi

echo "⏳ Waiting for Open WebUI to be ready... Press Enter to continue once it's ready."
read -r response < /dev/tty

# ─────────────────────────────────────────
# Step 1: Authenticate
# ─────────────────────────────────────────
echo "🔐 Authenticating..."
TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/auths/signin" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Authentication failed! Check your credentials."
  exit 1
fi
echo "✅ Authenticated successfully"

# ─────────────────────────────────────────
# Step 2: Create Knowledge Base
# ─────────────────────────────────────────
echo "📚 Creating Knowledge Base..."
KNOWLEDGE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/knowledge/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$KNOWLEDGE_NAME\",\"description\":\"$KNOWLEDGE_DESC\"}")

KNOWLEDGE_ID=$(echo "$KNOWLEDGE_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$KNOWLEDGE_ID" ]; then
  echo "❌ Failed to create Knowledge Base!"
  echo "Response: $KNOWLEDGE_RESPONSE"
  exit 1
fi
echo "✅ Knowledge Base created → ID: $KNOWLEDGE_ID"

# ─────────────────────────────────────────
# Step 3: Upload files and attach to KB
# ─────────────────────────────────────────
echo "📁 Starting file uploads from $FILES_DIR..."

for FILE_PATH in "$FILES_DIR"/*; do
  FILENAME=$(basename "$FILE_PATH")
  echo "📤 Uploading $FILENAME..."

  UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/files/" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$FILE_PATH")

  FILE_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

  if [ -z "$FILE_ID" ]; then
    echo "⚠️  Failed to upload $FILENAME — skipping"
    echo "Response: $UPLOAD_RESPONSE"
    continue
  fi
  echo "✅ Uploaded $FILENAME → File ID: $FILE_ID"

  # Attach file to Knowledge Base
  ATTACH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/knowledge/$KNOWLEDGE_ID/file/add" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"file_id\":\"$FILE_ID\"}")

  echo "✅ Attached $FILENAME to Knowledge Base"
done

# ─────────────────────────────────────────
# Step 4: Create Workspace Model
# ─────────────────────────────────────────
echo "🤖 Creating Workspace Model..."
MODEL_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/models/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$MODEL_ID\",
    \"name\": \"$MODEL_NAME\",
    \"base_model_id\": \"$BASE_MODEL\",
    \"meta\": {
      \"description\": \"$MODEL_DESC\",
      \"knowledge\": []
    },
    \"params\": {}
  }")

CREATED_MODEL_ID=$(echo "$MODEL_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$CREATED_MODEL_ID" ]; then
  echo "❌ Failed to create Model!"
  echo "Response: $MODEL_RESPONSE"
  exit 1
fi
echo "✅ Model created → ID: $CREATED_MODEL_ID"

# ─────────────────────────────────────────
# Step 5: Attach Knowledge Base to Model
# ─────────────────────────────────────────
echo "🔗 Attaching Knowledge Base to Model..."

UPDATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/models/model/update?id=$MODEL_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$MODEL_ID\",
    \"name\": \"$MODEL_NAME\",
    \"base_model_id\": \"$BASE_MODEL\",
    \"meta\": {
      \"description\": \"$MODEL_DESC\",
      \"knowledge\": [
        {
          \"id\": \"$KNOWLEDGE_ID\",
          \"name\": \"$KNOWLEDGE_NAME\",
          \"description\": \"$KNOWLEDGE_DESC\",
          \"type\": \"collection\"
        }
      ]
    },
    \"params\": {}
  }")

UPDATED_ID=$(echo "$UPDATE_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
if [ -z "$UPDATED_ID" ]; then
  echo "❌ Failed to attach Knowledge Base to Model!"
  echo "Response: $UPDATE_RESPONSE"
  exit 1
fi
echo "✅ Knowledge Base successfully attached to Model!"

# ─────────────────────────────────────────
# Summary
# ─────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Knowledge Base : $KNOWLEDGE_NAME"
echo "   ID             : $KNOWLEDGE_ID"
echo "🤖 Model Name     : $MODEL_NAME"
echo "   ID             : $CREATED_MODEL_ID"
echo "   Base Model     : $BASE_MODEL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"