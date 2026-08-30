-- Row-level isolation for agent reads, the Cloud SQL way:
-- parameterized secure views + an application role that can ONLY see the views.
--
-- The agent process never queries base tables. Every device/order/ticket read
-- goes through a view filtered by $@account, and the account value is supplied
-- by application code from verified identity (LiveKit token attribute or the
-- identification tool's result) — never by the language model.
--
-- Requires: cloudsql.enable_parameterized_views=on (instance flag, restart).

CREATE EXTENSION IF NOT EXISTS parameterized_views;
CREATE SCHEMA IF NOT EXISTS secure;

CREATE OR REPLACE VIEW secure.my_devices WITH (security_barrier) AS
  SELECT d.device_id, d.name, d.device_type, d.room, d.sku, d.installed_on
  FROM devices d JOIN customers c USING (customer_id)
  WHERE c.account_number = $@account;

CREATE OR REPLACE VIEW secure.my_orders WITH (security_barrier) AS
  SELECT o.order_id, o.item, o.sku, o.status, o.detail, o.placed_on, o.delivers_on
  FROM orders o JOIN customers c USING (customer_id)
  WHERE c.account_number = $@account;

CREATE OR REPLACE VIEW secure.my_tickets WITH (security_barrier) AS
  SELECT t.ticket_id, t.order_id, t.summary, t.status, t.opened_at
  FROM support_tickets t JOIN customers c USING (customer_id)
  WHERE c.account_number = $@account;

-- The role the web service uses for per-customer reads. No base-table access.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aria_app') THEN
    CREATE ROLE aria_app LOGIN;
  END IF;
END $$;
GRANT USAGE ON SCHEMA secure TO aria_app;
GRANT USAGE ON SCHEMA parameterized_views TO aria_app;
GRANT SELECT ON secure.my_devices, secure.my_orders, secure.my_tickets TO aria_app;
REVOKE ALL PRIVILEGES ON customers, subscriptions, devices, orders, support_tickets FROM aria_app;
REVOKE ALL ON SCHEMA public FROM aria_app;
GRANT USAGE ON SCHEMA public TO aria_app;  -- needed to resolve the extension's functions
