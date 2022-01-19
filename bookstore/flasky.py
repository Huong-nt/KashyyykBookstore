import os
import logging
from werkzeug.serving import WSGIRequestHandler, _log

from flask_migrate import Migrate
from app import create_app, db
from app.models import Role, User, RoleUser, Book

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        Role=Role,
        User=User,
        Book=Book,
        RoleUser=RoleUser,
    )


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
