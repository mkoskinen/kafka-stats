-- TODO: consider whether adding columns for the event time or host_id would make sense

CREATE TABLE stats_events (
    event_id SERIAL,
    data jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
