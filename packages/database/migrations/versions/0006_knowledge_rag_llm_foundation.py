"""AEGIS Enterprise Knowledge, RAG, and LLM Gateway Foundation Migration.

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-18 01:10:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    # 1. knowledge_sources
    op.create_table(
        'knowledge_sources',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.Column('tenant_id', sa.String(length=100), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_sources_source_type'), 'knowledge_sources', ['source_type'], unique=False)
    op.create_index(op.f('ix_knowledge_sources_tenant_id'), 'knowledge_sources', ['tenant_id'], unique=False)

    # 2. document_versions
    op.create_table(
        'document_versions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('parser_name', sa.String(length=100), nullable=False),
        sa.Column('chunk_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_versions_document_id'), 'document_versions', ['document_id'], unique=False)

    # 3. document_collections
    op.create_table(
        'document_collections',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tenant_id', sa.String(length=100), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('access_policy', sa.JSON(), nullable=False),
        sa.Column('document_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_collections_name'), 'document_collections', ['name'], unique=False)
    op.create_index(op.f('ix_document_collections_tenant_id'), 'document_collections', ['tenant_id'], unique=False)

    # 4. document_collection_members
    op.create_table(
        'document_collection_members',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('collection_id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_collection_members_collection_id'), 'document_collection_members', ['collection_id'], unique=False)
    op.create_index(op.f('ix_document_collection_members_document_id'), 'document_collection_members', ['document_id'], unique=False)

    # 5. document_chunks
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('section_title', sa.String(length=255), nullable=True),
        sa.Column('provenance_hash', sa.String(length=64), nullable=False),
        sa.Column('tenant_id', sa.String(length=100), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_chunks_provenance_hash'), 'document_chunks', ['provenance_hash'], unique=False)
    op.create_index(op.f('ix_document_chunks_tenant_id'), 'document_chunks', ['tenant_id'], unique=False)

    # 6. embedding_models
    op.create_table(
        'embedding_models',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('dimension', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_embedding_models_model_name'), 'embedding_models', ['model_name'], unique=False)

    # 7. embedding_records
    op.create_table(
        'embedding_records',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('chunk_id', sa.String(length=36), nullable=False),
        sa.Column('model_id', sa.String(length=36), nullable=False),
        sa.Column('vector_json', sa.JSON(), nullable=False),
        sa.Column('dimension', sa.Integer(), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=False),
        sa.Column('tenant_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_embedding_records_chunk_id'), 'embedding_records', ['chunk_id'], unique=False)

    # 8. knowledge_indexes
    op.create_table(
        'knowledge_indexes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('index_name', sa.String(length=255), nullable=False),
        sa.Column('index_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('document_count', sa.Integer(), nullable=False),
        sa.Column('chunk_count', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=100), nullable=False),
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. retrieval_queries
    op.create_table(
        'retrieval_queries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('retrieval_strategy', sa.String(length=50), nullable=False),
        sa.Column('top_k', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('execution_time_ms', sa.Float(), nullable=False),
        sa.Column('result_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. citations
    op.create_table(
        'citations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('rag_request_id', sa.String(length=36), nullable=False),
        sa.Column('citation_id', sa.String(length=100), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('version_id', sa.String(length=36), nullable=False),
        sa.Column('chunk_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('section_title', sa.String(length=255), nullable=True),
        sa.Column('excerpt', sa.Text(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. llm_providers & llm_model_registry & llm_requests
    op.create_table(
        'llm_providers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'llm_requests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('prompt_version_id', sa.String(length=36), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=False),
        sa.Column('output_tokens', sa.Integer(), nullable=False),
        sa.Column('total_tokens', sa.Integer(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('estimated_cost', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('tenant_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('llm_requests')
    op.drop_table('llm_providers')
    op.drop_table('citations')
    op.drop_table('retrieval_queries')
    op.drop_table('knowledge_indexes')
    op.drop_table('embedding_records')
    op.drop_table('embedding_models')
    op.drop_table('document_chunks')
    op.drop_table('document_collection_members')
    op.drop_table('document_collections')
    op.drop_table('document_versions')
    op.drop_table('knowledge_sources')
