"""initial schema - users, portfolio, learning

Revision ID: 001
Revises:
Create Date: 2026-07-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('username', sa.String(50), unique=True, nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('risk_tier', sa.String(50), server_default='beginner'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Risk Profiles
    op.create_table(
        'user_risk_profile',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), unique=True),
        sa.Column('risk_tolerance_score', sa.Integer(), default=0),
        sa.Column('knowledge_level', sa.Integer(), default=0),
        sa.Column('assessment_answers', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Sessions
    op.create_table(
        'user_session',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE')),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Portfolio
    op.create_table(
        'portfolio',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), unique=True),
        sa.Column('name', sa.String(100), server_default='Main Portfolio'),
        sa.Column('cash', sa.Float(), nullable=False, server_default='10000.0'),
        sa.Column('initial_capital', sa.Float(), nullable=False, server_default='10000.0'),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('is_default', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Holdings
    op.create_table(
        'holding',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('portfolio_id', sa.Integer(), sa.ForeignKey('portfolio.id', ondelete='CASCADE')),
        sa.Column('symbol', sa.String(10), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('shares', sa.Float(), nullable=False),
        sa.Column('avg_buy_price', sa.Float(), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Trades
    op.create_table(
        'trade',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('portfolio_id', sa.Integer(), sa.ForeignKey('portfolio.id', ondelete='CASCADE')),
        sa.Column('symbol', sa.String(10), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('side', sa.String(4), nullable=False),
        sa.Column('order_type', sa.String(20), server_default='market'),
        sa.Column('shares', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(20), server_default='filled'),
        sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Watchlists
    op.create_table(
        'watchlist',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE')),
        sa.Column('name', sa.String(100), nullable=False, server_default='My Watchlist'),
        sa.Column('is_default', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'watchlist_item',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('watchlist_id', sa.Integer(), sa.ForeignKey('watchlist.id', ondelete='CASCADE')),
        sa.Column('symbol', sa.String(10), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Learning Modules
    op.create_table(
        'learning_module',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tier', sa.String(50), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), server_default='5'),
        sa.Column('order_index', sa.Integer(), server_default='0'),
        sa.Column('content_url', sa.String(500), nullable=True),
        sa.Column('quiz_questions', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # User Module Progress
    op.create_table(
        'user_module_progress',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE')),
        sa.Column('module_id', sa.Integer(), sa.ForeignKey('learning_module.id', ondelete='CASCADE')),
        sa.Column('status', sa.String(20), server_default='not_started'),
        sa.Column('progress_pct', sa.Integer(), server_default='0'),
        sa.Column('quiz_score', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('user_module_progress')
    op.drop_table('learning_module')
    op.drop_table('watchlist_item')
    op.drop_table('watchlist')
    op.drop_table('trade')
    op.drop_table('holding')
    op.drop_table('portfolio')
    op.drop_table('user_session')
    op.drop_table('user_risk_profile')
    op.drop_table('user')
