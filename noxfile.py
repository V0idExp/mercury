import nox


PYTEST_VER = 'pytest>=5.3.5'
PYTEST_MOCK_VER = 'pytest-mock>=2.0.0'
FLAKE8_VER = 'flake8>=3.7.9'
COVERAGE_VER = 'coverage>=5.0.3'


@nox.session
def tests(session):
    """Run tests."""
    session.install('-r', 'requirements.txt')
    session.run('pytest')


@nox.session
def codestyle(session):
    """Check code style compliance."""
    session.install(FLAKE8_VER)
    session.run('flake8', '--max-line-length', '120', 'hg')


@nox.session
def coverage(session):
    """Run the tests and collect the code coverage statistics."""
    session.install('-r', 'requirements.txt')
    session.run('coverage', 'run', '--source', 'hg', '-m', 'pytest')
    session.run('coverage', 'html', '-d', 'coverage')
