Use Case Development
Let's start by creating detailed user stories that capture the core functionality. Here's how we can structure each use case:
Use Case: Document Upload and Processing
"As a user, I want to upload various types of documents so that I can organize and access them later"
Description: Users can upload documents through a simple drag-and-drop interface or file picker
Input: PDF files, images, audio recordings, or video clips (up to 100MB per file)
Output: Processed document with generated tags, extracted text, and embeddings
User Experience: The system shows upload progress and processing status in real-time
Constraints: Supported file formats, maximum file size, processing time limits
Use Case: Semantic Search
"As a user, I want to search across my uploaded content using natural language so that I can find relevant information quickly"
Description: Users can enter search queries in natural language and receive relevant results across all content types
Input: Text query (e.g., "Find documents about marketing strategy from last quarter")
Output: Ranked list of relevant documents with highlighted matches and context
User Experience: Results appear in real-time as users type, with visual previews where applicable
Constraints: Search latency requirements, result ranking accuracy
System Architecture
Let's separate the architecture into two main components:
Application Layer:

Web Server (FastAPI)

User authentication and session management
File upload handling
Search query processing
Chat interface management


Database Layer

MySQL for structured data (user info, document metadata)
File storage for raw documents
Qdrant for vector embeddings



ML Serving Layer:

Document Processing Service

Text extraction and preprocessing
Image analysis and feature extraction
Audio/video processing


Embedding Service

Text embedding generation
Image embedding generation
Audio embedding generation
Cross-modal alignment


LLM Service

Query understanding
Context retrieval
Response generation



Data Modeling
Let's design the core entities and their relationships:

User Entity

sqlCopyCREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP,
    last_login TIMESTAMP
);

Document Entity

sqlCopyCREATE TABLE documents (
    document_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    title VARCHAR(255),
    document_type ENUM('pdf', 'image', 'audio', 'video'),
    file_path VARCHAR(1024),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata JSONB
);

Tag Entity

sqlCopyCREATE TABLE tags (
    tag_id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(document_id),
    tag_type VARCHAR(50),
    tag_value VARCHAR(255),
    confidence FLOAT
);

Embedding Entity (Qdrant Schema)

pythonCopyclass EmbeddingPoint:
    id: UUID  # Matches document_id
    vector: List[float]  # Embedding vector
    payload: {
        'document_id': UUID,
        'chunk_index': int,
        'content_type': str,
        'metadata': Dict
    }