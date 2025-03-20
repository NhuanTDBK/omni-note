# Image Processing in Notes Application
## Description
Our image processing system transforms various types of images into searchable and interactive content. We handle multiple image types including bills, sketches, handwritten notes, and screenshots. The system combines computer vision and OCR technologies to extract maximum value from visual content while maintaining the original context and quality.

## Flow
The image processing pipeline consists of several sophisticated steps that convert raw images into searchable, categorized content:

### 1. Image Classification (https://github.com/michaelfeil/infinity for serving)
Our system uses a multi-stage classification approach:
1. **Primary Classification** 
   - Determines basic image type (bill, sketch, handwriting, screenshot, miscellaneous) (google/siglip-large-patch16-256)
   - Uses CNN-based image classification
   - Considers image properties (resolution, color depth, aspect ratio)

2. **Secondary Analysis** (pydantic structured output)
   - For bills: Identifies vendor, date, amount
   - For sketches: Determines subject matter, style
   - For handwriting: Analyzes writing style, layout
   - For screenshots: Identifies source application, content type, operating system

### 2. Tag Generation
Tags are generated through a comprehensive analysis:
1. **Visual Feature Analysis**
   - Color schemes and patterns
   - Object detection results
   - Text content (if present)
   - Layout analysis

2. **Context Integration**
   - Matches with existing tag database
   - Creates new tags based on unique features
   - Considers user-specific tag patterns

### 3. Text Extraction
The system employs different strategies based on image type:
1. **Bills and Documents**
   - High-precision OCR for structured text
   - Field detection (amounts, dates, headers)
   - Table structure recognition

2. **Handwritten Content**
   - Handwriting recognition with language model integration
   - Context-aware text correction
   - Layout preservation

3. **Screenshots**
   - UI element detection
   - Text layer extraction
   - Interface context preservation

### 4. Embedding Generation
Multi-modal embedding generation includes:
1. **Visual Embeddings**
   - Generated from image features
   - Object-level embeddings
   - Scene understanding vectors

2. **Text Embeddings**
   - Generated from extracted text
   - Combined with visual context
   - Optimized for cross-modal retrieval

## Example
Let's follow the processing of a receipt image:

1. **Classification**:
   ```python
   image_analysis = {
       'type': 'image',
       'subtype': 'receipt',
       'confidence': 0.96,
       'properties': {
           'vendor_detected': True,
           'total_amount_present': True,
           'date_present': True
       }
   }
   ```

2. **Text Extraction**:
   ```python
   extracted_content = {
       'vendor': 'Whole Foods Market',
       'date': '2024-02-21',
       'total_amount': '$156.78',
       'location': 'Austin, TX',
       'line_items': [
           {'item': 'Organic Apples', 'amount': '$4.99'},
           // Additional items
       ]
   }
   ```

3. **Tag Generation**:
   ```python
   generated_tags = [
       'receipt',
       'grocery',
       'whole_foods',
       'food_expense',
       'february_2024'
   ]
   ```

4. **Embedding Generation**:
   ```python
   embeddings = {
       'visual_embedding': [...],  # Visual features vector
       'text_embedding': [...],    # Text content vector
       'combined_embedding': [...], # Multi-modal embedding
       'chunk_reference': {
           'type': 'full_document',
           'id': 'receipt_20240221_001'
       }
   }
   ```

This processed image is now ready for multi-modal search and chat interactions, supporting both visual and text-based queries.