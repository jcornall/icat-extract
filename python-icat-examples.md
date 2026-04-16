To start with, include these two files in the same directory:

icat.cfg
```
[isis]
url = https://icat.isis.stfc.ac.uk
auth = anon
```

main.py
```
from icat.config import Config

config = Config()
client, cfg = config.getconfig()
client.login(cfg.auth, cfg.credentials)
print(client.search("select f from Facility f"))
```

Running this with `python main.py -s isis` should print the ISIS facility information retrieved from our ICAT instance.

The 'anon' authenticator is used for publicly accessible data, and will include everything that's not under embargo AKA everything that's at least 3 years old.

---

Probably the core object in ICAT is Investigation, which represents a single experiment. It's possible to retrieve all investigations with something like this:

```
for inv in client.searchChunked("Investigation order by id desc"):
    print(inv)
```

There are ~180k of these at the moment, ~170k of which are visible to the anon user.

Conditions can be applied, e.g. to filter down to just user experiments:

```
query = "SELECT i from Investigation i where i.type.id = 4 order by i.id desc"
for inv in client.searchChunked(query):
    print(inv)
```

---

By default objects come 'flat', meaning that they don't include any of the objects which are linked to them. Use the `include` keyword in the query to fetch any related entities of interest, e.g. this:

```
query = "select i from Investigation i where i.id = 22369015 include i.datasets.datafiles"
inv = client.search(query)
print(inv[0].datasets[0].datafiles)
```

Outputs all the datafiles connected to a particular experiment.

---

Other tools:

 - https://icatadmin.netlify.app/ is a gui tool we use for interacting with icat data. You should be able to login using the details in `icat.cfg` and be able to browse
 - python-icat also comes with the [icatdump](https://python-icat.readthedocs.io/en/stable/icatdump.html) script, which might be useful for doing a 'full' export, though I've never used it and eyeballing it it looks like it's basically just running a query for each of the tables so I don't think it's any more efficient, and there are warnings about it potentially being incorrect if the data in ICAT changes whilst it's running
