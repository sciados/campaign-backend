pip install -r requirements.txt
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: fastapi==0.104.1 in c:\users\shaun\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from -r requirements.txt (line 2)) (0.104.1)
Requirement already satisfied: uvicorn==0.24.0 in c:\users\shaun\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from uvicorn[standard]==0.24.0->-r requirements.txt (line 3)) (0.24.0)
Requirement already satisfied: python-dotenv==1.0.0 in c:\users\shaun\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from -r requirements.txt (line 6)) (1.0.0)
Requirement already satisfied: pydantic>=2.8.0 in c:\users\shaun\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from -r requirements.txt (line 7)) (2.10.6)
Requirement already satisfied: email-validator==2.1.0 in c:\users\shaun\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from -r requirements.txt (line 8)) (2.1.0)
Requirement already satisfied: asyncpg==0.29.0 in c:\users\shaun\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from -r requirements.txt (line 11)) (0.29.0)
Requirement already satisfied: sqlalchemy==2.0.23 in c:\users\shaun\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from -r requirements.txt (line 12)) (2.0.23)
Requirement already satisfied: alembic==1.12.1 in c:\users\shaun\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages (from -r requirements.txt (line 13)) (1.12.1)
Collecting psycopg2-binary==2.9.6 (from -r requirements.txt (line 14))
  Using cached psycopg2-binary-2.9.6.tar.gz (384 kB)
  Preparing metadata (setup.py) ... error
  error: subprocess-exited-with-error

  × python setup.py egg_info did not run successfully.
  │ exit code: 1
  ╰─> [36 lines of output]
      C:\Users\shaun\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\setuptools\dist.py:759: SetuptoolsDeprecationWarning: License classifiers are deprecated.
      !!

              ********************************************************************************
              Please consider removing the following classifiers in favor of a SPDX license expression:

              License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)

              See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license for details.
              ********************************************************************************

      !!
        self._finalize_license_expression()
      running egg_info
      creating C:\Users\shaun\AppData\Local\Temp\pip-pip-egg-info-5bijdjcn\psycopg2_binary.egg-info
      writing C:\Users\shaun\AppData\Local\Temp\pip-pip-egg-info-5bijdjcn\psycopg2_binary.egg-info\PKG-INFO
      writing dependency_links to C:\Users\shaun\AppData\Local\Temp\pip-pip-egg-info-5bijdjcn\psycopg2_binary.egg-info\dependency_links.txt
      writing top-level names to C:\Users\shaun\AppData\Local\Temp\pip-pip-egg-info-5bijdjcn\psycopg2_binary.egg-info\top_level.txt
      writing manifest file 'C:\Users\shaun\AppData\Local\Temp\pip-pip-egg-info-5bijdjcn\psycopg2_binary.egg-info\SOURCES.txt'

      Error: pg_config executable not found.

      pg_config is required to build psycopg2 from source.  Please add the directory
      containing pg_config to the $PATH or specify the full executable path with the
      option:

          python setup.py build_ext --pg-config /path/to/pg_config build ...

      or with the pg_config option in 'setup.cfg'.

      If you prefer to avoid building psycopg2 from source, please install the PyPI
      'psycopg2-binary' package instead.

      For further information please check the 'doc/src/install.rst' file (also at
      <https://www.psycopg.org/docs/install.html>).

      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
error: metadata-generation-failed

× Encountered error while generating package metadata.
╰─> See above for output.

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.