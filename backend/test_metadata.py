"""Test metadata extraction and filtering."""

from agent.rag import initialize_rag

rag = initialize_rag()

print('Testing metadata extraction:')
print('='*80)

# Test 1: Search for Meta specifically
docs = rag.vectorstore.similarity_search('questions', k=5, filter={'company': {'$eq': 'meta'}})
print(f'\nFound {len(docs)} Meta documents')
if docs:
    print(f'Sample Meta doc metadata: {docs[0].metadata}')
    print(f'Content preview: {docs[0].page_content[:200]}...')

print()
print('-'*80)

# Test 2: Search for easy difficulty
docs = rag.vectorstore.similarity_search('questions', k=5, filter={'difficulty': {'$eq': 'easy'}})
print(f'\nFound {len(docs)} Easy difficulty documents')
if docs:
    print(f'Sample Easy doc metadata: {docs[0].metadata}')
    print(f'Content preview: {docs[0].page_content[:200]}...')

print()
print('-'*80)

# Test 3: Search for Meta + Easy
filter_both = {
    '$and': [
        {'company': {'$eq': 'meta'}},
        {'difficulty': {'$eq': 'easy'}}
    ]
}
docs = rag.vectorstore.similarity_search('questions', k=5, filter=filter_both)
print(f'\nFound {len(docs)} Meta + Easy documents')
if docs:
    print(f'Sample Meta Easy doc metadata: {docs[0].metadata}')
    print(f'Content preview: {docs[0].page_content[:300]}...')

print()
print('='*80)
print('✅ Metadata extraction working!' if docs else '❌ Metadata extraction not working')

