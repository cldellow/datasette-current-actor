# datasette-current-actor

[![PyPI](https://img.shields.io/pypi/v/datasette-current-actor.svg)](https://pypi.org/project/datasette-current-actor/)
[![Changelog](https://img.shields.io/github/v/release/cldellow/datasette-current-actor?include_prereleases&label=changelog)](https://github.com/cldellow/datasette-current-actor/releases)
[![Tests](https://github.com/cldellow/datasette-current-actor/workflows/Test/badge.svg)](https://github.com/cldellow/datasette-current-actor/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/cldellow/datasette-current-actor/blob/main/LICENSE)

Adds a `current_actor()` function to SQLite that show's the current actor's ID.

## Installation

Install this plugin in the same environment as Datasette.

    datasette install datasette-current-actor

## Usage

### Boring mode

`SELECT current_actor()` returns `NULL` if there's no currently-logged in actor,
or the id of the actor.

You could put this in a canned query to provide limited access to tables.

### Ludicrous mode

SQLite is _flexible_. It turns out you can refer to functions that don't exist
when issuing DDL statements. As long as they exist when they're needed, it all
works out.

#### Auditing

Track who added a row:

```sql
CREATE TABLE notes(
  created_by text not null default (current_actor()),
  note text not null
);
```

Or create an UPDATE trigger on a table that sets the `last_edited_by` column to
`current_actor()`.

#### Row-level security

Restrict the rows that users see:

```sql
CREATE VIEW rls AS
SELECT * FROM sensitive_data WHERE owner = current_actor()
```

You can see a live example at https://dux.fly.dev/cooking/my_questions, which should show you 0 rows.

That instance permits "logging in" by passing a `_whoami` query parameter. If you visit https://dux.fly.dev/cooking/my_questions?_whoami=15, you'll see all of user 15's questions.



## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-current-actor
    python3 -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
