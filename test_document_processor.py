"""
Test the document processor with sample files.
"""
from document_processor import ingest_document


print("=" * 60)
print("Testing Document Processor")
print("=" * 60)

# Test 1: Plain text file
print("\n📄 Test 1: Ingesting sample_ai_policy.txt")
print("-" * 60)
result = ingest_document(
    "sample_ai_policy.txt",
    claimed_purpose="AI Use Policy"
)
print(f"Filename: {result.filename}")
print(f"Type: {result.file_type}")
print(f"Size: {result.file_size_bytes} bytes")
print(f"Claimed purpose: {result.claimed_purpose}")
print(f"Page/line count: {result.page_count}")
print(f"Warnings: {result.extraction_warnings or '(none)'}")
print(f"\nFirst 300 chars of extracted text:")
print(f"  {result.extracted_text[:300]}")
print(f"\nTotal extracted text length: {len(result.extracted_text)} chars")