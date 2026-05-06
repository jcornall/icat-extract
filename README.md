# icat-extract

A Python package for querying ICAT via a CLI and extracting investigation data for processing. 
The module uses the `python-icat` package to connect to and query ICAT. 

## Installing icat-extract

Clone the repository, install and activate a virtual environment, then finally install the dependencies:

```bash
python -m venv .venv
srouce .venv/bin/activate
pip install -e .
```

Verify the installation by executing this command:

```bash
icat-extract --help
```

## Configuring icat-extract

`icat-extract` requires a configuration file, `config.yaml`, to operate correctly, however this must be created separately. Once created, it is recommended that it be stored in the root of the project directory. 

You can view an example of what `config.yaml` should look like in the `examples/` folder.

When running `icat-extract`, you will need to specify the path to the config file using the `--config` flag:

```bash
icat-extract --config config.yaml
```

### Handling secrets

Secrets, such as the ICAT username and password, are resolved from environment variables. You will need to set these prior to running any queries.

```bash
export ICAT_USERNAME=<USERNAME>
export ICAT_PASSWORD=<PASSWORD>
```

## Running icat-extract

icat-extract can be used via the CLI. Currently, you can filter your queries using the following flags:

- --start-date
- --instrument
- --rb-number

You can also control whether ICAT displays additional data from the ICAT data graph, using INCLUDE statements:

- --include

`icat-extract` includes default query profiles allowing you to quickly include data to varying levels of detail. These are listed in `config.yaml`, and can be customised:

- --include-profile

For a full list and description of each flag, use the `--help` flag:

```bash
icat-extract --help
```

## Querying ICAT

### Filtering

#### By RB number

A simple command that returns basic results for a single experiment (RB number):

```bash
icat-extract --config config.yaml \
    --rb-number 2220008
```

#### By instrument

If you want to search for investigations using a specific instrument:

```bash
icat-extract --config config.yaml \
    --instrument HRPD
```

#### By start date

If you want to search for investigations that started after a specific date:

```bash
icat-extract --config config.yaml \
    --start-date 2024-01-01
```

### Including objects

#### Implicitly (using profiles)

ICAT queries have the option of including related data - this can expand the amount of data available to the user. To make things simpler, `icat-extract` supports "INCLUDE" profiles, which allow the user to control the level of granularity in their searches. 

| Profile | Description |
| --- | --- |
| `minimal` | Safe for wide queries (quick) |
| `medium ` | Uses common metadata |
| `full` | Includes the full investigation data graph (expensive)

```bash
icat-extract --config config.yaml \
    --include-profile medium
```

Users are free to customise these profiles in the `config.yaml` file.

### Explicitly (using flags)

You can also use the `--include` flag to explicitly include data graph objects in your query, without using the `config.yaml` "INCLUDE" profiles.

```bash
icat-extract --config config.yaml \
    --include i.facility \
    --include i.datasets \
    --include i.samples.parameters
```

### Limitations

By default, unbounded queries that use deep "INCLUDE" statements (such as those querying `datasets`, `samples`) require the selective filters listed above. These can be expensive for ICAT and may result in failed queries and timeouts. 

If you wish to override these checks, use the `--force` flag.

```bash
icat-extract --config config.yaml \
    --include-profile full \
    --force
```

## Outputs

### Customising the output location

By default, query results are written to `/results`.

For usage with a data lake, you can specify the desired output filepath in your `config.yaml`:

```yaml
output:
    lake_root: /srv/data-lake
```

Finally, you can specify an output location for your query run using the `--output-dir` flag:

```bash
icat-extract --config config.yaml \
    --output-dir 
```

## Logging

### File logging

icat-extract defaults to outputting logs to the console using `stderr`. Optionally, you can write logs to a file using the `--log-file` flag:

```bash
icat-extract --config config.yaml \
    --log-file /logs
```

You can also enable DEBUG-level logs using the `--verbose` flag:

```bash
icat-extract --config config.yaml \
    --verbose
```