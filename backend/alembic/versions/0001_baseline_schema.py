"""baseline schema

Revision ID: 0001
Revises:
Create Date: 2026-02-06

All tables as of initial Alembic adoption.
This migration uses create_all-style approach for the baseline.
Future migrations will be incremental ALTER statements.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- branches ---
    op.create_table('branches',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('subdomain', sa.String(100)),
        sa.Column('phone', sa.String(20)),
        sa.Column('address', sa.String(500)),
        sa.Column('theme_primary_color', sa.String(7), server_default='#d4af37'),
        sa.Column('theme_bg_color', sa.String(7), server_default='#1a1a1a'),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('opening_time', sa.Time),
        sa.Column('closing_time', sa.Time),
        sa.Column('last_order_time', sa.Time),
        sa.Column('closed_days', sa.JSON),
        sa.Column('max_capacity', sa.Integer, server_default='30'),
        sa.Column('features', sa.JSON),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_branches_code', 'branches', ['code'])

    # --- global_customers ---
    op.create_table('global_customers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('phone', sa.String(20), nullable=False, unique=True),
        sa.Column('name', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_global_customers_phone', 'global_customers', ['phone'])

    # --- branch_customers ---
    op.create_table('branch_customers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('global_customer_id', sa.String(36), sa.ForeignKey('global_customers.id'), nullable=False),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('visit_count', sa.Integer, server_default='0'),
        sa.Column('last_visit', sa.DateTime(timezone=True)),
        sa.Column('is_vip', sa.Boolean, server_default=sa.text('0')),
        sa.Column('notes', sa.String(1000)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_branch_customers_branch', 'branch_customers', ['branch_code'])

    # --- customer_preferences ---
    op.create_table('customer_preferences',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_customer_id', sa.String(36), sa.ForeignKey('branch_customers.id'), nullable=False),
        sa.Column('preference', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50)),
        sa.Column('note', sa.String(500)),
        sa.Column('confidence', sa.Float, server_default='1.0'),
        sa.Column('source', sa.String(50), server_default="'manual'"),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- staff ---
    op.create_table('staff',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('employee_id', sa.String(20), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('name_kana', sa.String(255)),
        sa.Column('phone', sa.String(20)),
        sa.Column('email', sa.String(255)),
        sa.Column('role', sa.String(20), server_default="'waiter'"),
        sa.Column('pin_code', sa.String(6)),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('1')),
        sa.Column('hire_date', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_staff_branch', 'staff', ['branch_code'])

    # --- tables ---
    op.create_table('tables',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('table_number', sa.String(10), nullable=False),
        sa.Column('name', sa.String(100)),
        sa.Column('min_capacity', sa.Integer, server_default='1'),
        sa.Column('max_capacity', sa.Integer, nullable=False),
        sa.Column('table_type', sa.String(20), server_default="'regular'"),
        sa.Column('floor', sa.Integer, server_default='1'),
        sa.Column('zone', sa.String(50)),
        sa.Column('has_window', sa.Boolean, server_default=sa.text('0')),
        sa.Column('is_smoking', sa.Boolean, server_default=sa.text('0')),
        sa.Column('is_wheelchair_accessible', sa.Boolean, server_default=sa.text('1')),
        sa.Column('has_baby_chair', sa.Boolean, server_default=sa.text('0')),
        sa.Column('status', sa.String(20), server_default="'available'"),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('1')),
        sa.Column('priority', sa.Integer, server_default='0'),
        sa.Column('notes', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_tables_branch', 'tables', ['branch_code'])

    # --- bookings ---
    op.create_table('bookings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('branch_customer_id', sa.String(36), sa.ForeignKey('branch_customers.id')),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('time', sa.String(5), nullable=False),
        sa.Column('guests', sa.Integer, nullable=False),
        sa.Column('guest_name', sa.String(255)),
        sa.Column('guest_phone', sa.String(20)),
        sa.Column('guest_email', sa.String(255)),
        sa.Column('status', sa.String(20), server_default="'pending'"),
        sa.Column('note', sa.String(1000)),
        sa.Column('staff_note', sa.String(1000)),
        sa.Column('checked_in_at', sa.DateTime(timezone=True)),
        sa.Column('source', sa.String(50), server_default="'web'"),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_bookings_branch', 'bookings', ['branch_code'])
    op.create_index('ix_bookings_date', 'bookings', ['date'])

    # --- table_assignments ---
    op.create_table('table_assignments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('booking_id', sa.String(36), sa.ForeignKey('bookings.id'), nullable=False),
        sa.Column('table_id', sa.String(36), sa.ForeignKey('tables.id'), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('seated_at', sa.DateTime(timezone=True)),
        sa.Column('cleared_at', sa.DateTime(timezone=True)),
        sa.Column('notes', sa.String(500)),
    )
    op.create_index('ix_table_assignments_booking', 'table_assignments', ['booking_id'])
    op.create_index('ix_table_assignments_table', 'table_assignments', ['table_id'])

    # --- table_availability ---
    op.create_table('table_availability',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('table_id', sa.String(36), sa.ForeignKey('tables.id'), nullable=False),
        sa.Column('date', sa.DateTime, nullable=False),
        sa.Column('time_slot', sa.String(5), nullable=False),
        sa.Column('is_available', sa.Boolean, server_default=sa.text('1')),
        sa.Column('booking_id', sa.String(36), sa.ForeignKey('bookings.id')),
    )
    op.create_index('ix_table_availability_branch', 'table_availability', ['branch_code'])
    op.create_index('ix_table_availability_date', 'table_availability', ['date'])

    # --- menu_items (legacy) ---
    op.create_table('menu_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100)),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('subcategory', sa.String(50)),
        sa.Column('display_order', sa.Integer, server_default='0'),
        sa.Column('price', sa.Numeric(10, 0), nullable=False),
        sa.Column('tax_rate', sa.Numeric(4, 2), server_default='10.0'),
        sa.Column('image_url', sa.String(500)),
        sa.Column('prep_time_minutes', sa.Integer, server_default='5'),
        sa.Column('kitchen_note', sa.String(200)),
        sa.Column('is_available', sa.Boolean, server_default=sa.text('1')),
        sa.Column('is_popular', sa.Boolean, server_default=sa.text('0')),
        sa.Column('is_spicy', sa.Boolean, server_default=sa.text('0')),
        sa.Column('is_vegetarian', sa.Boolean, server_default=sa.text('0')),
        sa.Column('allergens', sa.String(200)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_menu_items_branch', 'menu_items', ['branch_code'])
    op.create_index('ix_menu_items_category', 'menu_items', ['category'])

    # --- item_categories ---
    op.create_table('item_categories',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100)),
        sa.Column('description', sa.Text),
        sa.Column('parent_id', sa.String(36), sa.ForeignKey('item_categories.id')),
        sa.Column('display_order', sa.Integer, server_default='0'),
        sa.Column('icon', sa.String(50)),
        sa.Column('image_url', sa.String(500)),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_item_categories_branch', 'item_categories', ['branch_code'])

    # --- items (enhanced) ---
    op.create_table('items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('category_id', sa.String(36), sa.ForeignKey('item_categories.id')),
        sa.Column('sku', sa.String(50), unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100)),
        sa.Column('description', sa.Text),
        sa.Column('base_price', sa.Numeric(10, 0), nullable=False),
        sa.Column('tax_rate', sa.Numeric(4, 2), server_default='10.0'),
        sa.Column('prep_time_minutes', sa.Integer, server_default='5'),
        sa.Column('kitchen_printer', sa.String(50)),
        sa.Column('kitchen_note', sa.Text),
        sa.Column('display_order', sa.Integer, server_default='0'),
        sa.Column('image_url', sa.String(500)),
        sa.Column('is_available', sa.Boolean, server_default=sa.text('1')),
        sa.Column('is_popular', sa.Boolean, server_default=sa.text('0')),
        sa.Column('is_spicy', sa.Boolean, server_default=sa.text('0')),
        sa.Column('is_vegetarian', sa.Boolean, server_default=sa.text('0')),
        sa.Column('allergens', sa.String(200)),
        sa.Column('has_options', sa.Boolean, server_default=sa.text('0')),
        sa.Column('options_required', sa.Boolean, server_default=sa.text('0')),
        sa.Column('track_stock', sa.Boolean, server_default=sa.text('0')),
        sa.Column('stock_quantity', sa.Integer),
        sa.Column('low_stock_alert', sa.Integer),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_items_branch', 'items', ['branch_code'])

    # --- item_option_groups ---
    op.create_table('item_option_groups',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100)),
        sa.Column('description', sa.Text),
        sa.Column('selection_type', sa.String(20), nullable=False, server_default="'single'"),
        sa.Column('min_selections', sa.Integer, server_default='0'),
        sa.Column('max_selections', sa.Integer, server_default='1'),
        sa.Column('display_order', sa.Integer, server_default='0'),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_option_groups_branch', 'item_option_groups', ['branch_code'])

    # --- item_options ---
    op.create_table('item_options',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('group_id', sa.String(36), sa.ForeignKey('item_option_groups.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100)),
        sa.Column('price_adjustment', sa.Numeric(10, 0), server_default='0'),
        sa.Column('is_default', sa.Boolean, server_default=sa.text('0')),
        sa.Column('display_order', sa.Integer, server_default='0'),
        sa.Column('is_available', sa.Boolean, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    # --- item_option_assignments ---
    op.create_table('item_option_assignments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('item_id', sa.String(36), sa.ForeignKey('items.id'), nullable=False),
        sa.Column('option_group_id', sa.String(36), sa.ForeignKey('item_option_groups.id'), nullable=False),
        sa.Column('display_order', sa.Integer, server_default='0'),
    )

    # --- combos ---
    op.create_table('combos',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_en', sa.String(200)),
        sa.Column('description', sa.Text),
        sa.Column('discount_type', sa.String(20), nullable=False),
        sa.Column('discount_value', sa.Numeric(10, 2), nullable=False),
        sa.Column('start_date', sa.Date),
        sa.Column('end_date', sa.Date),
        sa.Column('valid_hours_start', sa.Time),
        sa.Column('valid_hours_end', sa.Time),
        sa.Column('valid_days', sa.String(50)),
        sa.Column('max_uses_total', sa.Integer),
        sa.Column('max_uses_per_order', sa.Integer, server_default='1'),
        sa.Column('current_uses', sa.Integer, server_default='0'),
        sa.Column('min_order_amount', sa.Numeric(10, 0)),
        sa.Column('display_order', sa.Integer, server_default='0'),
        sa.Column('image_url', sa.String(500)),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('1')),
        sa.Column('is_featured', sa.Boolean, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_combos_branch', 'combos', ['branch_code'])

    # --- combo_items ---
    op.create_table('combo_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('combo_id', sa.String(36), sa.ForeignKey('combos.id'), nullable=False),
        sa.Column('item_id', sa.String(36), sa.ForeignKey('items.id')),
        sa.Column('category_id', sa.String(36), sa.ForeignKey('item_categories.id')),
        sa.Column('quantity', sa.Integer, server_default='1'),
    )

    # --- promotions ---
    op.create_table('promotions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_en', sa.String(200)),
        sa.Column('description', sa.Text),
        sa.Column('trigger_type', sa.String(30), nullable=False),
        sa.Column('trigger_item_id', sa.String(36), sa.ForeignKey('items.id')),
        sa.Column('trigger_category_id', sa.String(36), sa.ForeignKey('item_categories.id')),
        sa.Column('trigger_value', sa.Numeric(10, 0), nullable=False),
        sa.Column('reward_type', sa.String(30), nullable=False),
        sa.Column('reward_item_id', sa.String(36), sa.ForeignKey('items.id')),
        sa.Column('reward_value', sa.Numeric(10, 2)),
        sa.Column('reward_quantity', sa.Integer, server_default='1'),
        sa.Column('start_date', sa.Date),
        sa.Column('end_date', sa.Date),
        sa.Column('valid_hours_start', sa.Time),
        sa.Column('valid_hours_end', sa.Time),
        sa.Column('valid_days', sa.String(50)),
        sa.Column('max_uses_per_order', sa.Integer, server_default='1'),
        sa.Column('max_uses_per_customer', sa.Integer),
        sa.Column('max_uses_total', sa.Integer),
        sa.Column('current_uses', sa.Integer, server_default='0'),
        sa.Column('stackable', sa.Boolean, server_default=sa.text('0')),
        sa.Column('priority', sa.Integer, server_default='0'),
        sa.Column('display_order', sa.Integer, server_default='0'),
        sa.Column('image_url', sa.String(500)),
        sa.Column('show_on_menu', sa.Boolean, server_default=sa.text('1')),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_promotions_branch', 'promotions', ['branch_code'])

    # --- promotion_usages ---
    op.create_table('promotion_usages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('promotion_id', sa.String(36), sa.ForeignKey('promotions.id'), nullable=False),
        sa.Column('order_id', sa.String(36), nullable=False),
        sa.Column('customer_id', sa.String(36)),
        sa.Column('discount_amount', sa.Numeric(10, 0), nullable=False),
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- orders ---
    op.create_table('orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('table_id', sa.String(36), nullable=False),
        sa.Column('session_id', sa.String(36), nullable=False),
        sa.Column('order_number', sa.Integer, nullable=False),
        sa.Column('status', sa.String(20), server_default="'pending'"),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('confirmed_at', sa.DateTime(timezone=True)),
        sa.Column('ready_at', sa.DateTime(timezone=True)),
        sa.Column('served_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_orders_branch', 'orders', ['branch_code'])
    op.create_index('ix_orders_table', 'orders', ['table_id'])
    op.create_index('ix_orders_session', 'orders', ['session_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])

    # --- order_items ---
    op.create_table('order_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('order_id', sa.String(36), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('menu_item_id', sa.String(36), nullable=False),
        sa.Column('item_name', sa.String(100), nullable=False),
        sa.Column('item_price', sa.Numeric(10, 0), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False, server_default='1'),
        sa.Column('notes', sa.String(200)),
        sa.Column('status', sa.String(20), server_default="'pending'"),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('prepared_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_order_items_order', 'order_items', ['order_id'])

    # --- table_sessions ---
    op.create_table('table_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('table_id', sa.String(36), sa.ForeignKey('tables.id'), nullable=False),
        sa.Column('booking_id', sa.String(36), sa.ForeignKey('bookings.id')),
        sa.Column('guest_count', sa.Integer, server_default='1'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(timezone=True)),
        sa.Column('is_paid', sa.Boolean, server_default=sa.text('0')),
        sa.Column('total_amount', sa.Numeric(10, 0), server_default='0'),
        sa.Column('notes', sa.Text),
    )
    op.create_index('ix_table_sessions_branch', 'table_sessions', ['branch_code'])
    op.create_index('ix_table_sessions_table', 'table_sessions', ['table_id'])

    # --- chat_messages ---
    op.create_table('chat_messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('branch_customer_id', sa.String(36), sa.ForeignKey('branch_customers.id')),
        sa.Column('session_id', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.String(5000), nullable=False),
        sa.Column('insights_extracted', sa.Boolean, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_chat_messages_branch', 'chat_messages', ['branch_code'])
    op.create_index('ix_chat_messages_session', 'chat_messages', ['session_id'])

    # --- chat_insights ---
    op.create_table('chat_insights',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_customer_id', sa.String(36), sa.ForeignKey('branch_customers.id')),
        sa.Column('message_id', sa.String(36), sa.ForeignKey('chat_messages.id')),
        sa.Column('insight_type', sa.String(50)),
        sa.Column('insight_value', sa.String(500)),
        sa.Column('confidence', sa.String(10)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- order_events ---
    op.create_table('order_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_source', sa.String(30), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('table_id', sa.String(36)),
        sa.Column('session_id', sa.String(36)),
        sa.Column('order_id', sa.String(36)),
        sa.Column('order_item_id', sa.String(36)),
        sa.Column('actor_type', sa.String(20)),
        sa.Column('actor_id', sa.String(36)),
        sa.Column('data', sa.JSON),
        sa.Column('correlation_id', sa.String(36)),
        sa.Column('sequence_number', sa.Integer),
        sa.Column('error_code', sa.String(50)),
        sa.Column('error_message', sa.Text),
    )
    op.create_index('ix_order_events_type', 'order_events', ['event_type'])
    op.create_index('ix_order_events_source', 'order_events', ['event_source'])
    op.create_index('ix_order_events_timestamp', 'order_events', ['timestamp'])
    op.create_index('ix_order_events_branch', 'order_events', ['branch_code'])
    op.create_index('ix_order_events_table', 'order_events', ['table_id'])
    op.create_index('ix_order_events_session', 'order_events', ['session_id'])
    op.create_index('ix_order_events_order', 'order_events', ['order_id'])
    op.create_index('ix_order_events_correlation', 'order_events', ['correlation_id'])
    op.create_index('ix_order_events_session_time', 'order_events', ['session_id', 'timestamp'])
    op.create_index('ix_order_events_order_time', 'order_events', ['order_id', 'timestamp'])
    op.create_index('ix_order_events_corr_seq', 'order_events', ['correlation_id', 'sequence_number'])
    op.create_index('ix_order_events_type_time', 'order_events', ['event_type', 'timestamp'])

    # --- waiting_list ---
    op.create_table('waiting_list',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('customer_name', sa.String(255), nullable=False),
        sa.Column('customer_phone', sa.String(20)),
        sa.Column('guest_count', sa.Integer, nullable=False),
        sa.Column('queue_number', sa.Integer, nullable=False),
        sa.Column('status', sa.String(20), server_default="'waiting'"),
        sa.Column('estimated_wait_minutes', sa.Integer),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('called_at', sa.DateTime(timezone=True)),
        sa.Column('seated_at', sa.DateTime(timezone=True)),
        sa.Column('assigned_table_id', sa.String(36), sa.ForeignKey('tables.id')),
        sa.Column('note', sa.String(500)),
    )
    op.create_index('ix_waiting_list_branch', 'waiting_list', ['branch_code'])
    op.create_index('ix_waiting_list_status', 'waiting_list', ['status'])

    # --- checkin_logs ---
    op.create_table('checkin_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('branch_code', sa.String(50), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('booking_id', sa.String(36), sa.ForeignKey('bookings.id')),
        sa.Column('waiting_id', sa.String(36), sa.ForeignKey('waiting_list.id')),
        sa.Column('table_id', sa.String(36), sa.ForeignKey('tables.id')),
        sa.Column('customer_name', sa.String(255)),
        sa.Column('guest_count', sa.Integer),
        sa.Column('event_data', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_checkin_logs_branch', 'checkin_logs', ['branch_code'])
    op.create_index('ix_checkin_logs_type', 'checkin_logs', ['event_type'])


def downgrade() -> None:
    op.drop_table('checkin_logs')
    op.drop_table('waiting_list')
    op.drop_table('order_events')
    op.drop_table('chat_insights')
    op.drop_table('chat_messages')
    op.drop_table('table_sessions')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('promotion_usages')
    op.drop_table('promotions')
    op.drop_table('combo_items')
    op.drop_table('combos')
    op.drop_table('item_option_assignments')
    op.drop_table('item_options')
    op.drop_table('item_option_groups')
    op.drop_table('items')
    op.drop_table('item_categories')
    op.drop_table('menu_items')
    op.drop_table('table_availability')
    op.drop_table('table_assignments')
    op.drop_table('bookings')
    op.drop_table('tables')
    op.drop_table('staff')
    op.drop_table('customer_preferences')
    op.drop_table('branch_customers')
    op.drop_table('global_customers')
    op.drop_table('branches')
