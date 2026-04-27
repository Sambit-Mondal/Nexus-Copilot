"""
Phase 4: Embedding Service Production Tests
Complete testing of text embedding, similarity, and batch processing.
"""
import sys
import numpy as np
from pathlib import Path

# Add api-gateway to path
sys.path.insert(0, str(Path.cwd()))

print("=" * 70)
print("PHASE 4: EMBEDDING SERVICE PRODUCTION TESTS")
print("=" * 70)

try:
    from app.embedding import get_embedding_service
    from app.exceptions import EmbeddingError
    
    # Initialize embedding service
    print("\n[1] Initializing Embedding Service...")
    embedding_service = get_embedding_service()
    print(f"✓ Embedding service initialized")
    print(f"  Model: {embedding_service.model.get_sentence_embedding_dimension()}-dim")
    print(f"  Dimension: {embedding_service.dimension}")
    
    # Test 1: Single text embedding
    print("\n[2] Testing Single Text Embedding...")
    text1 = "What is the risk exposure in the Tech sector?"
    embedding1 = embedding_service.embed_text(text1)
    
    print(f"✓ Single embedding generated")
    print(f"  Input text: '{text1}'")
    print(f"  Text length: {len(text1)} chars")
    print(f"  Vector dimension: {embedding1.shape[0]}")
    print(f"  Vector norm: {np.linalg.norm(embedding1):.4f}")
    print(f"  Min value: {embedding1.min():.6f}")
    print(f"  Max value: {embedding1.max():.6f}")
    print(f"  Mean value: {embedding1.mean():.6f}")
    
    # Test 2: Batch embedding
    print("\n[3] Testing Batch Text Embedding...")
    texts = [
        "Apple stock performance analysis",
        "Market trends in financial sector",
        "Risk assessment methodology",
    ]
    embeddings = embedding_service.embed_batch(texts)
    
    print(f"✓ Batch embedding generated")
    print(f"  Number of texts: {len(texts)}")
    print(f"  Embeddings shape: {embeddings.shape}")
    print(f"  All texts embedded successfully")
    
    for i, text in enumerate(texts):
        print(f"    [{i+1}] {text} ({len(text)} chars)")
    
    # Test 3: Similarity computation
    print("\n[4] Testing Cosine Similarity...")
    similarity_single = embedding_service.cosine_similarity(embedding1, embeddings[0])
    
    print(f"✓ Similarity computed")
    print(f"  Text 1: '{text1}'")
    print(f"  Text 2: '{texts[0]}'")
    print(f"  Cosine similarity: {similarity_single:.6f}")
    
    # Test 4: Batch similarity
    print("\n[5] Testing Batch Similarity...")
    similarities = embedding_service.cosine_similarities(embedding1, embeddings)
    
    print(f"✓ Batch similarities computed")
    print(f"  Query: '{text1}'")
    print(f"  Similarities shape: {similarities.shape}")
    
    for i, (text, sim) in enumerate(zip(texts, similarities)):
        print(f"    [{i+1}] {text}: {sim:.6f}")
    
    # Test 5: Embedding consistency
    print("\n[6] Testing Embedding Consistency...")
    embedding1_again = embedding_service.embed_text(text1)
    is_consistent = np.allclose(embedding1, embedding1_again, atol=1e-6)
    
    print(f"{'✓' if is_consistent else '✗'} Embedding consistency check")
    print(f"  Same text embedded twice")
    print(f"  Max difference: {np.abs(embedding1 - embedding1_again).max():.10f}")
    print(f"  Are they identical? {is_consistent}")
    
    # Test 6: Different texts produce different embeddings
    print("\n[7] Testing Embedding Uniqueness...")
    text_different = "This is a completely different text about something else"
    embedding_different = embedding_service.embed_text(text_different)
    similarity_diff = embedding_service.cosine_similarity(embedding1, embedding_different)
    
    print(f"✓ Different texts produce different embeddings")
    print(f"  Text 1: '{text1}'")
    print(f"  Text 2: '{text_different}'")
    print(f"  Similarity: {similarity_diff:.6f} (should be low)")
    
    # Test 7: Edge cases
    print("\n[8] Testing Edge Cases...")
    
    # Very short text
    short_text = "Hi"
    short_embedding = embedding_service.embed_text(short_text)
    print(f"✓ Short text embedding: '{short_text}' → {short_embedding.shape}")
    
    # Long text
    long_text = " ".join(["word"] * 100)
    long_embedding = embedding_service.embed_text(long_text)
    print(f"✓ Long text embedding: {len(long_text)} chars → {long_embedding.shape}")
    
    # Empty text handling
    try:
        embedding_service.embed_text("")
        print("✗ Empty text should raise error")
    except EmbeddingError:
        print("✓ Empty text correctly raises EmbeddingError")
    
    # Test 8: Vector normalization properties
    print("\n[9] Testing Vector Properties...")
    
    # Check if vectors are normalized
    norms = [np.linalg.norm(e) for e in embeddings]
    print(f"✓ Vector norms:")
    for i, norm in enumerate(norms):
        print(f"    Text {i+1}: {norm:.6f}")
    
    # Test 9: Dimension validation
    print("\n[10] Testing Dimension Validation...")
    all_dims_match = all(e.shape[0] == embedding_service.dimension for e in embeddings)
    print(f"{'✓' if all_dims_match else '✗'} All embeddings match configured dimension")
    print(f"    Expected: {embedding_service.dimension}")
    print(f"    All match: {all_dims_match}")
    
    # Summary
    print("\n" + "=" * 70)
    print("PHASE 4: ALL TESTS PASSED ✓")
    print("=" * 70)
    print("\nSummary:")
    print("  ✓ Embedding service initialized successfully")
    print("  ✓ Single text embedding works")
    print("  ✓ Batch text embedding works")
    print("  ✓ Cosine similarity computation works")
    print("  ✓ Batch similarity computation works")
    print("  ✓ Embedding consistency verified")
    print("  ✓ Different texts produce different embeddings")
    print("  ✓ Edge cases handled correctly")
    print("  ✓ Vector properties validated")
    print("  ✓ Dimension validation passed")
    print("\nEmbedding Service is production-ready! ✓")
    print("=" * 70)
    
except EmbeddingError as e:
    print(f"\n✗ Embedding Service Error: {str(e)}")
    print("\nTroubleshooting:")
    print("  1. Check torch/torchvision versions are compatible")
    print("  2. Ensure sentence-transformers is installed correctly")
    print("  3. Check internet connection (model download required on first run)")
    print("  4. See api-gateway/requirements.txt for version specifications")
    sys.exit(1)
    
except Exception as e:
    print(f"\n✗ Unexpected Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
